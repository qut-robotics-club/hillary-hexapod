import UrdfViewer from "../lib/urdf-viewer-element";
import styled, { css } from "styled-components";
import { useState, useEffect, useRef, MutableRefObject } from "react";
import { Api } from "../ts/api";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

customElements.define("urdf-viewer", UrdfViewer);

const useRobot = (ref: MutableRefObject<UrdfViewer>, api: Api) => {
  const [robot, setRobot] = useState(null);

  useEffect(() => {
    const viewer = ref.current;
    if (viewer !== undefined && viewer.robot !== null) {
      setRobot(viewer.robot);
      const joints = viewer.robot.joints;

      api.onJointStateUpdate(update => {
        for (const jointName in update) {
          joints[jointName].setAngle(update[jointName]);
        }
        viewer.redraw();
      });
      // test - move all joints a random amount 10 times a second
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
    props.calibrating
      ? css`
          left: 0;
          right: 30vw;
          bottom: 0;
        `
      : css`
          left: 20vw;
          right: 40vw;
          bottom: 60vh;
        `}
`;

const ExitButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background-color: transparent;
  border: none;
  color: black;
  cursor: pointer;
  font-size: 18px;
  z-index: 20;
`;

export default ({
  api,
  ref = useRef<UrdfViewer>(),
  _robot: robot = useRobot(ref, api),
  _calibratingState: [calibrating, setCalibrating] = useState(false)
}) => (
  <Container calibrating={calibrating}>
    {calibrating ? (
      <ExitButton onClick={() => setCalibrating(false)}>
        <FontAwesomeIcon icon={faTimes} />
      </ExitButton>
    ) : null}
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
