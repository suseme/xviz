
# Generated XVIZ for a scenario that is a
# straight path with relative horizontal lines
# for movement indication
# - no start end time in metadata
# - no streams in metadata
#   - this means primitives have the coordinate IDENTITY
#

import math
import time

import xviz_avs as xviz
from xviz_avs.v2.session_pb2 import StateUpdate

DEG_1_AS_RAD = math.pi / 180


class StraightScenario:
    def __init__(self, live=True, line_gap=5, duration=10, speed=10):
        self._metadata = None
        self._timestamp = time.time()   # timestamp needs to be seconds, not milliseconds
        self._line_gap = line_gap
        self._duration = duration
        self._speed = speed     # meters per second
        self._live = live

    def get_metadata(self):
        if not self._metadata:
            builder = xviz.XVIZMetadataBuilder()
            builder.stream("/vehicle_pose").category(xviz.CATEGORY.POSE)
            builder.stream('/ground_lines') \
                .coordinate(xviz.COORDINATE_TYPES.IDENTITY) \
                .category(xviz.CATEGORY.PRIMITIVE) \
                .type(xviz.PRIMITIVE_TYPES.POLYLINE) \
                .stream_style({
                    'stroked': True,
                    'stroke_width': 0.2
                })

            self._metadata = builder.get_message()

        metadata = {
            'type': 'xviz/metadata',
            'data': self._metadata.to_object()
        }

        if not self._live:
            log_start_time = self._timestamp
            metadata['data']['log_info'] = {
                "log_start_time": log_start_time,
                "log_end_time": log_start_time + self._duration
            }

        print('metadata', metadata)

        return metadata

    def get_message(self, time_offset):
        timestamp = self._timestamp + time_offset

        builder = xviz.XVIZBuilder(metadata=self._metadata)

        return self._get_message(builder, timestamp)

    def _get_message(self, builder, timestamp):

        # TODO: draw everything
        x = self._get_position_x(timestamp)
        self._draw_poses(builder, timestamp, x)
        self._draw_lines(builder, x)

        builder._update_type = StateUpdate.UpdateType.SNAPSHOT

        # output data
        data = builder.get_message()

        message = {
            'type': 'xviz/state_update',
            'data': data.to_object()
        }

        print('message', message)

        return message

    def _draw_poses(self, builder, timestamp, x):
        builder.pose('/vehicle_pose') \
            .timestamp(timestamp) \
            .orientation(0, 0, 0) \
            .position(x, 0, 0)

    def _range(self, start, end, increment=1):
        l_spacing = []
        for i in range(start, end, increment):
            l_spacing.append(i * self._line_gap)
        return l_spacing

    def _line_color(self, x):
        # Generate cyclical colors
        return [
            int(120 + math.cos(x * 2 * DEG_1_AS_RAD) * 90),
            int(200 + math.cos(x * DEG_1_AS_RAD) * 30),
            int(170 + math.cos(x * 3 * DEG_1_AS_RAD) * 60)
        ]

    def _get_position_x(self, timestamp):
        return self._speed * (timestamp - self._timestamp)

    def _draw_lines(self, builder, x):
        # Car position matches the messageNumber
        # place the farthest 20
        line_start = (x - 15) / self._line_gap
        line_end = (x + 20) / self._line_gap

        line_spacing = self._range(math.ceil(line_start), math.floor(line_end))

        for line_x in line_spacing:
            builder.primitive('/ground_lines') \
                .polyline([line_x, -40, 0, line_x, 40, 0]) \
                .style({
                    'stroke_color': self._line_color(line_x)
                })

