'''
Generated XVIZ for a scenario that is a circular path on a grid
- no start end time in metadata
- stream metadata for coordinate & styling
'''

import math
import time

import xviz_avs as xviz
from xviz_avs.v2.session_pb2 import StateUpdate

DEG_1_AS_RAD = math.pi / 180

class OrbitScenario:
    def __init__(self, live=True, radius=30, duration=10, speed=10):
        self._metadata = None
        self._timestamp = time.time()   # timestamp needs to be seconds, not milliseconds
        self._radius = radius
        self._duration = duration
        self._speed = speed # meters per second
        self._live = live

        self._first = True

    def get_metadata(self):
        if not self._metadata:
            builder = xviz.XVIZMetadataBuilder()
            builder.stream("/vehicle_pose").category(xviz.CATEGORY.POSE)
            builder.stream("/system").category(xviz.CATEGORY.POSE)
            builder.stream("/earth_orbit").category(xviz.CATEGORY.POSE)
            builder.stream("/moon_orbit").category(xviz.CATEGORY.POSE)
            builder.stream("/mars_orbit").category(xviz.CATEGORY.POSE)
            builder.stream("/sun_pose").category(xviz.CATEGORY.POSE)
            builder.stream("/earth_pose").category(xviz.CATEGORY.POSE)
            builder.stream("/moon_pose").category(xviz.CATEGORY.POSE)
            builder.stream("/mars_pose").category(xviz.CATEGORY.POSE)
            builder.stream('/sun').category(xviz.CATEGORY.PRIMITIVE) \
                .type(xviz.PRIMITIVE_TYPES.CIRCLE)
            builder.stream('/earth').category(xviz.CATEGORY.PRIMITIVE) \
                .type(xviz.PRIMITIVE_TYPES.CIRCLE)
            builder.stream('/moon').category(xviz.CATEGORY.PRIMITIVE) \
                .type(xviz.PRIMITIVE_TYPES.CIRCLE)
            builder.stream('/mars').category(xviz.CATEGORY.PRIMITIVE) \
                .type(xviz.PRIMITIVE_TYPES.CIRCLE)

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

        if self._first:
            self._first = False
            return self._get_first_message(builder, time_offset)
        return self._get_message(builder, time_offset)

    def _get_first_message(self, builder, time_offset):
        timestamp = self._timestamp + time_offset

        # draw everything
        self._draw_poses(builder, timestamp)
        self._draw_links(builder, timestamp)
        self._draw_orbs(builder, timestamp)

        builder._update_type = StateUpdate.UpdateType.PERSISTENT

        # output data
        data = builder.get_message()

        message = {
            'type': 'xviz/state_update',
            'data': data.to_object()
        }

        print('message', message)

        return message

    def _get_message(self, builder, time_offset):
        timestamp = self._timestamp + time_offset

        # TODO: draw everything
        self._draw_dynamic_poses(builder, timestamp)
        self._draw_dynamic_links(builder, timestamp)

        builder._update_type = StateUpdate.UpdateType.INCREMENTAL

        # output data
        data = builder.get_message()

        message = {
            'type': 'xviz/state_update',
            'data': data.to_object()
        }

        print('message', message)

        return message

    def _draw_poses(self, builder, timestamp):
        builder.pose("/vehicle_pose") \
            .timestamp(timestamp) \
            .orientation(0, 0, 0) \
            .position(0, 0, 0)

        builder.pose("/system") \
            .timestamp(timestamp) \
            .orientation(0, 0, 0) \
            .position(0, 0, 0)

    def _draw_links(self, builder, timestamp):
        builder.link('/system', '/sun_pose')
        builder.link('/system', '/earth_orbit')
        builder.link('/system', '/mars_orbit')
        builder.link('/sun_pose', '/sun')
        builder.link('/earth_orbit', '/earth_pose')
        builder.link('/earth_pose', '/earth')
        builder.link('/moon_orbit', '/moon_pose')
        builder.link('/moon_pose', '/moon')
        builder.link('/mars_orbit', '/mars_pose')
        builder.link('/mars_pose', '/mars')

    def _draw_orbs(self, builder, timestamp):
        builder.primitive('/sun').circle([0.0, 0.0, 0.0], 9) \
            .style({'fill_color': [255, 180, 40]})
        builder.primitive('/earth').circle([0.0, 0.0, 0.0], 5) \
            .style({'fill_color': [20, 50, 190]})
        builder.primitive('/moon').circle([0.0, 0.0, 0.0], 1) \
            .style({'fill_color': [200, 200, 200]})
        builder.primitive('/mars').circle([0.0, 0.0, 0.0], 4) \
            .style({'fill_color': [255, 0, 0]})

    def _draw_dynamic_poses(self, builder, timestamp):
        degreesPerSecond = 45
        currentDegrees = timestamp * degreesPerSecond
        angle = currentDegrees * DEG_1_AS_RAD

        # FIXME: must update the timestamp of '/vehicle_pose', for the default timestamp used in builder.
        builder.pose('/vehicle_pose') \
            .timestamp(timestamp)

        builder.pose('/earth_orbit') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(0, 0, 0)
        builder.pose('/moon_orbit') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(0, 0, 0)
        builder.pose('/mars_orbit') \
            .timestamp(timestamp) \
            .orientation(0, 0, -angle) \
            .position(0, 0, 0)

        builder.pose('/sun_pose') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(0, 0, 0)
        builder.pose('/earth_pose') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(25, 0, 0)
        builder.pose('/moon_pose') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(10, 0, 0)
        builder.pose('/mars_pose') \
            .timestamp(timestamp) \
            .orientation(0, 0, angle) \
            .position(50, 0, 0)

    def _draw_dynamic_links(self, builder, timestamp):
        cycle = timestamp % 10
        if cycle > 5:
            builder.link('/moon_orbit', '/mars_pose')
        else:
            builder.link('/moon_orbit', '/earth_pose')
