import UrdfViewer from "../lib/urdf-viewer-element";
import styled, { css } from "styled-components";
import { useState, useEffect, useRef, MutableRefObject } from "react";
import { Api } from "../ts/api";

customElements.define("urdf-viewer", UrdfViewer);

const useRobot = (ref: MutableRefObject<UrdfViewer>, api: Api) => {
  const [robot, setRobot] = useState(null);

  useEffect(() => {
    const viewer = ref.current;
    if (viewer !== undefined && viewer.robot !== null) {
      const joints = viewer.robot.joints;

      // api.onJointStateUpdate(jointState => {
      //   // console.log("jointState", jointState);
      // });
      // test - move all joints a random amount 10 times a second

      setInterval(() => {
        console.log("randomly changing angles");
        for (const name in joints) {
          joints[name].setAngle(joints[name].angle + Math.random() - 0.5);
        }
        viewer.redraw();
      }, 1000);
    }
  }, [ref.current && ref.current.robot]);

  return robot;
};

const Container = styled.div`
  position: absolute;
  top: 0;
  z-index: 10;
  background-color: white;

  transition: all 0.5s;
  ${props =>
    props.fullscreen
      ? css`
          left: 0;
          right: 0;
          bottom: 0;
        `
      : css`
          left: 25vw;
          right: 50vw;
          bottom: 70vh;
        `}
`;

export default ({
  api,
  ref = useRef<UrdfViewer>(),
  _robot: robot = useRobot(ref, api)
}) => (
  <Container>
    <urdf-viewer
      ref={ref}
      up="+Z"
      display-shadow
      tabindex="0"
      urdf="/static/urdf/crab.urdf"
      style={{ width: "100%", height: "100%" }}
    ></urdf-viewer>
  </Container>
);
