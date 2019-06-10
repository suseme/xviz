// Copyright (c) 2019 Uber Technologies, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/* global Buffer */
/* eslint-disable camelcase */
import {XVIZROSBag} from '@xviz/ros';
import {XVIZUIBuilder} from '@xviz/builder';

// We subclass from the XVIZROSBag
// and override the `initMetadata` to add our own
// entries for UI elements.
export class PaccarBag extends XVIZROSBag {
  constructor(bagPath, topicConfig) {
    super(bagPath, topicConfig);
  }

  // could override and skip this entirely
  async initMetadata(context, ros2xviz) {
    const metadata = await super.initMetadata(context, ros2xviz);
    const FORWARD_CENTER = '/vehicle/camera/center_front';

    const ui = new XVIZUIBuilder({});
    const panel = ui.panel({
      name: 'Metrics'
    });
    const container = ui.container({
      name: 'Metrics Panel',
      layout: 'vertical'
    });
    const metricVelocity = ui.metric({
      title: 'Velocity',
      streams: ['/vehicle/velocity'],
      description: 'The velocity of the vehicle'
    });

    container.child(metricVelocity);
    panel.child(container);
    ui.child(panel);
 
    const cam_panel = ui.panel({
      name: 'Camera'
    });

    const video = ui.video({
      cameras: [FORWARD_CENTER]
    });

    cam_panel.child(video);
    ui.child(cam_panel);

    metadata.data.ui_config = ui.getUI();
    return metadata;
  }
}