import UrdfViewer from "../lib/urdf-viewer-element";
import styled, { css } from "styled-components";
import { useState, useEffect, useRef, MutableRefObject } from "react";

customElements.define('urdf-viewer', UrdfViewer)


const useRobot = (ref: MutableRefObject<UrdfViewer>) => {
  const [robot, setRobot] = useState(null);

  useEffect(() => {
    if (ref.current !== undefined) {
      const viewer = ref.current;

    }
  }, [ref.current])

  return robot;
}

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
  ref = useRef<UrdfViewer>(),
  _robot: robot = useRobot(ref)
}) => <Container>
    <urdf-viewer ref={ref} up="+Z" display-shadow tabindex="0" urdf="/static/urdf/crab.urdf" style={{ width: "100%", height: "100%" }}></urdf-viewer>
  </Container>