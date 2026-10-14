#!/usr/bin/env bash

# Start the same active components as run_all.sh, but use an RTSP/live source.
# Usage: ./run_all_live.sh 'rtsp://user:password@camera.example:554/stream1' [base_csv]

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 'rtsp://user:password@camera.example:554/stream1' [base_csv]" >&2
    exit 64
fi

STREAM_URL="$1"
BASE_FILE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SETUP_SCRIPT="${WORKSPACE_DIR}/install/setup.bash"
LAUNCH_FILE="${SCRIPT_DIR}/launch/deepstream_live.py"

if [[ ! -f "${SETUP_SCRIPT}" ]]; then
    echo "ROS workspace setup file not found: ${SETUP_SCRIPT}" >&2
    echo "Build from ${WORKSPACE_DIR} first: colcon build --packages-select video_streamer_cpp" >&2
    exit 1
fi

if [[ ! -f "${LAUNCH_FILE}" ]]; then
    echo "Live-stream launch file not found: ${LAUNCH_FILE}" >&2
    exit 1
fi

# Pass values as positional arguments to bash rather than interpolating them into
# shell source. This keeps RTSP characters such as !, &, ?, and @ intact.
gnome-terminal --title="RTSP Image View" -- bash -c \
    'source "$1"; ros2 run rqt_image_view rqt_image_view; exec bash' \
    bash "${SETUP_SCRIPT}"
sleep 2

if [[ -n "${BASE_FILE}" ]]; then
    gnome-terminal --title="CSV Subscriber" -- bash -c \
        'source "$1"; ros2 run inputCSVSubscriber inputCSVSubscriber "$2"; exec bash' \
        bash "${SETUP_SCRIPT}" "${BASE_FILE}"
else
    gnome-terminal --title="CSV Subscriber" -- bash -c \
        'source "$1"; ros2 run inputCSVSubscriber inputCSVSubscriber; exec bash' \
        bash "${SETUP_SCRIPT}"
fi
sleep 5

gnome-terminal --title="RTSP DeepStream" -- bash -c \
    'source "$1"; ros2 launch "$2" "video_path:=$3" backend:=ffmpeg; exec bash' \
    bash "${SETUP_SCRIPT}" "${LAUNCH_FILE}" "${STREAM_URL}"
