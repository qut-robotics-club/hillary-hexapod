import ReactJoystick from "react-joystick";
import styled from "styled-components";
import { useState } from "react";

import Menu from "./Menu";
// import LiveStream from "./LiveStream";
import UrdfViewer from '../components/UrdfViewer'

import { useMockApi as useApi } from "../ts/api";

const App = styled.div`
  font-family: Impact, Charcoal, sans-serif;
`;

const Container = styled.div`
  display: flex;
  align-items: stretch;
  height: 100vh;
  > * {
    flex-grow: 1;
  }
`;

const LeftSide = styled.div`
  position: relative;
`;

const RightSide = styled.div`
  display: flex;
  flex-direction: column;
`;

const JoystickContainer = styled.div`
  display: flex;
  position: relative;
  align-items: center;
  justify-content: center;

  > span {
    color: #757575;
    position: absolute;
    z-index: 1;

    font-size: 2rem;
    white-space: pre-line;
    text-align: center;

    user-select: none;
    pointer-events: none;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  align-items: stretch;
  height: 50vh;
  button {
    cursor: pointer;
    flex-grow: 1;
    color: white;

    border: ${pressed => (pressed ? "5px solid #EEEEEE" : "3px solid #424242")};
  }
`;

const KickButton = styled.button`
  flex-grow: 1;
  background-image: linear-gradient(to bottom left, #f44336, #b71c1c);
  font-size: 10vh;

  :hover {
    background-image: linear-gradient(to bottom left, #b71c1c, #f44336);
  }
  :active {
    border-color: #b71c1c;
  }
`;

const ConfigButtons = styled.div`
  display: flex;
  flex-direction: column;
  font-size: 0.75em;
`;

const ToggleDribbleButton = styled.button`
  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);
  font-size: 3vh;

  :hover {
    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);
  }
  :active {
    border-color: #0d47a1;
  }

  ${({ on }) => (on ? "" : "filter: grayscale(100%)")}
`;

const MenuButton = styled.button`
  background-image: linear-gradient(to bottom left, #4caf50, #1b5e20);
  font-size: 7vh;

  :hover {
    background-image: linear-gradient(to bottom left, #1b5e20, #4caf50);
  }
  :active {
    border-color: #388e3c;
  }
`;

const Joystick = ({ height: height = "auto", bgText, onMove, onEnd }) => (
  <JoystickContainer>
    <span>{bgText}</span>
    <ReactJoystick
      joyOptions={{
        mode: "semi",
        catchDistance: 100,
        color: "white"
      }}
      containerStyle={{
        display: "flex",
        position: "relative",
        margin: 0,
        background: "radial-gradient(#212121, #212121, #424242)",
        height,
        width: "50vw",
        justifyContent: "center",
        alignItems: "center"
      }}
      managerListener={nipple => {
        nipple.on("move", onMove);
        nipple.on("end", onEnd);
      }}
    />
  </JoystickContainer>
);

export default ({
  _dribbleState: [isDribbling, setDribbling] = useState(false),
  _menuState: [isMenuOpen, setMenuOpen] = useState(false),
  _motionState: [{ x, y, omega }, _setDesiredMotion] = useState({
    x: 0,
    y: 0,
    omega: 0
  }),
  api = useApi(),
  setDesiredMotion = (x, y, omega) => {
    api.setDesiredMotion(x, y, omega); // update server state via websocket
    _setDesiredMotion({ x, y, omega }); // update client state via react hook
  }
}) =>
  api ? (
    <App>
      {isMenuOpen ? (
        <Menu onClose={() => setMenuOpen(false)} api={api} />
      ) : null}
      <Container>
        <UrdfViewer />

        <LeftSide>
          <Joystick
            height="100vh"
            bgText={`↑
          ← STRAFE →
          ↓`}
            onMove={(_, stick) => {
              const MAX_STICK_DIST = 50;
              const angle = stick.angle.radian;
              const unitMagnitude = stick.distance / MAX_STICK_DIST;
              const x = unitMagnitude * Math.cos(angle);
              const y = unitMagnitude * Math.sin(angle);
              setDesiredMotion(x, y, omega);
            }}
            onEnd={() => setDesiredMotion(0, 0, omega)}
          />
        </LeftSide>

        <RightSide>
          <Joystick
            height="50vh"
            bgText="↶ ROTATE ↷"
            onMove={(_, stick) => {
              const MAX_STICK_DIST = 50;
              const angle = stick.angle.radian;
              const unitMagnitude = stick.distance / MAX_STICK_DIST;
              const omega = unitMagnitude * Math.cos(angle);
              setDesiredMotion(x, y, omega);
            }}
            onEnd={() => setDesiredMotion(x, y, 0)}
          />

          <ButtonContainer>
            <ConfigButtons>
              <ToggleDribbleButton
                onClick={() => {
                  api.setDribbling(!isDribbling);
                  setDribbling(!isDribbling);
                }}
                className={isDribbling ? "on" : null}
                on={isDribbling}
              >
                TOGGLE
                <br />
                DRIBBLE:
                <br />
                {isDribbling ? "ON" : "OFF"}
              </ToggleDribbleButton>
              <MenuButton onClick={() => setMenuOpen(true)}>MENU</MenuButton>
            </ConfigButtons>
            <KickButton onClick={api.kick}>
              <b>KICK</b>
            </KickButton>
          </ButtonContainer>
        </RightSide>
      </Container>
    </App>
  ) : (
      <p>Creating a live connection to the robot...</p>
    );
