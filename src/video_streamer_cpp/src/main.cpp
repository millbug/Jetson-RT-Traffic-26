#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <opencv2/opencv.hpp>
#include <image_transport/image_transport.hpp>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <stdexcept>
#include <string>

class VideoStreamer : public rclcpp::Node
{
public:
    VideoStreamer()
    : Node("video_streamer")
    {
        // `video_filepath` is retained for existing launch files. `source` may
        // be a local file or a URI such as rtsp://user:password@camera/stream.
        declare_parameter<std::string>("video_filepath", "");
        declare_parameter<std::string>("source", "");
        declare_parameter<std::string>("backend", "auto");
        declare_parameter<int>("fps", 30);
        declare_parameter("width", 960);
        declare_parameter("height", 544);
        declare_parameter<int>("reconnect_delay_ms", 1000);

        width_ = get_parameter("width").as_int();
        height_ = get_parameter("height").as_int();
        const int fps = get_parameter("fps").as_int();
        const auto reconnect_delay_ms = get_parameter("reconnect_delay_ms").as_int();

        if (fps <= 0 || width_ <= 0 || height_ <= 0 || reconnect_delay_ms < 0) {
            throw std::invalid_argument(
                "fps, width, and height must be positive; reconnect_delay_ms cannot be negative");
        }
        reconnect_delay_ = std::chrono::milliseconds(reconnect_delay_ms);

        source_ = get_parameter("source").as_string();
        if (source_.empty()) {
            source_ = get_parameter("video_filepath").as_string();
        }
        if (source_.empty()) {
            throw std::invalid_argument("Set 'source' (or legacy 'video_filepath') to a file or stream URI");
        }

        live_source_ = is_live_source(source_);
        backend_ = backend_from_name(get_parameter("backend").as_string());
        if (!open_capture()) {
            if (!live_source_) {
                throw std::runtime_error("Failed to open video source: " + source_);
            }
            RCLCPP_WARN(this->get_logger(),
                "Cannot open live source '%s'; retrying every %ld ms",
                source_.c_str(), reconnect_delay_.count());
            next_reconnect_time_ = std::chrono::steady_clock::now() + reconnect_delay_;
        }

        image_pub_ = image_transport::create_publisher(this, "image_raw");

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(1000 / fps),
            std::bind(&VideoStreamer::publish_frame, this)
        );
    }

private:
    static bool is_live_source(const std::string & source)
    {
        const auto scheme_end = source.find("://");
        if (scheme_end == std::string::npos) {
            return false;
        }
        std::string scheme = source.substr(0, scheme_end);
        std::transform(scheme.begin(), scheme.end(), scheme.begin(),
            [](unsigned char character) { return static_cast<char>(std::tolower(character)); });
        return scheme == "rtsp" || scheme == "rtsps" || scheme == "rtmp" ||
               scheme == "udp" || scheme == "srt" || scheme == "http" || scheme == "https";
    }

    static int backend_from_name(const std::string & backend)
    {
        if (backend == "auto") {
            return cv::CAP_ANY;
        }
        if (backend == "ffmpeg") {
            return cv::CAP_FFMPEG;
        }
        if (backend == "gstreamer") {
            return cv::CAP_GSTREAMER;
        }
        throw std::invalid_argument("backend must be 'auto', 'ffmpeg', or 'gstreamer'");
    }

    bool open_capture()
    {
        cap_.release();
        const bool opened = cap_.open(source_, backend_);
        if (opened) {
            RCLCPP_INFO(this->get_logger(), "Opened %s source '%s' with backend %s",
                live_source_ ? "live" : "file", source_.c_str(),
                cap_.getBackendName().c_str());
        }
        return opened;
    }

    void publish_frame()
    {
        if (!cap_.isOpened()) {
            if (std::chrono::steady_clock::now() >= next_reconnect_time_ && !open_capture()) {
                next_reconnect_time_ = std::chrono::steady_clock::now() + reconnect_delay_;
            }
            return;
        }

        cv::Mat frame;
        if (!cap_.read(frame)) {
            if (!live_source_) {
                RCLCPP_INFO(this->get_logger(), "Video finished. Looping...");
                cap_.set(cv::CAP_PROP_POS_FRAMES, 0);
                return;
            }

            RCLCPP_WARN(this->get_logger(), "Lost live stream '%s'; reconnecting", source_.c_str());
            cap_.release();
            next_reconnect_time_ = std::chrono::steady_clock::now() + reconnect_delay_;
            return;
        }
        cv::Mat output_frame;
        cv::resize(frame, output_frame, cv::Size(width_, height_));
        
        cv::Mat rgb_frame;
        cv::cvtColor(output_frame, rgb_frame, cv::COLOR_BGR2RGB);

        std_msgs::msg::Header header;
        header.stamp = this->now();
        sensor_msgs::msg::Image::SharedPtr msg = cv_bridge::CvImage(
           header, "rgb8", rgb_frame
        ).toImageMsg();

        // sensor_msgs::msg::Image::SharedPtr msg = cv_bridge::CvImage(
        //     std_msgs::msg::Header(), "bgr8", frame
        // ).toImageMsg();

        image_pub_.publish(msg);
    }

    cv::VideoCapture cap_;
    image_transport::Publisher image_pub_;
    rclcpp::TimerBase::SharedPtr timer_;

    std::string source_;
    bool live_source_;
    int backend_;
    std::chrono::milliseconds reconnect_delay_;
    std::chrono::steady_clock::time_point next_reconnect_time_{};
    int width_;
    int height_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<VideoStreamer>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
