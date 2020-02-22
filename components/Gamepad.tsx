import ReactJoystick from "react-joystick";
import styled from "styled-components";
import { useState } from "react";
import Rodal from "rodal";

import "antd/dist/antd.css";
import "rodal/lib/rodal.css";
// import LiveStream from "./LiveStream";
import UrdfViewer from "../components/UrdfViewer";
import { Slider, Checkbox } from "antd";

import { useApi } from "../ts/api";

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

const CalibrationPanel = styled.div`
  color: #757575;
  background-color: #424242;
  position: absolute;
  right: 0;
  left: 70vw;
  font-family: Calibri;
  top: 0;
  height: 100vh;
  overflow: scroll;
  padding: 5px;
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
  // _dribbleState: [isDribbling, setDribbling] = useState(false),
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
  },
  _calibratorsState: [calibrators, setCalibrators] = useState<{
    [name: string]: [number, number, number, boolean]; // servoIdx, min, max, isReversed
  }>(null)
}) =>
  api ? (
    <App>
      <Container>
        <UrdfViewer
          api={api}
          _calibratingState={[
            calibrators !== null,
            calibrating => {
              if (!calibrating) {
                setCalibrators(null);
              }
            }
          ]}
        />
        {calibrators ? (
          <CalibrationPanel>
            <h2>Calibration</h2>
            {Object.entries(calibrators).map(
              ([name, [_, min, max, isReversed]]) => (
                <div key={name}>
                  {name}
                  <Checkbox
                    checked={isReversed}
                    onChange={e => {
                      const isReversed = e.target.checked;
                      calibrators[name][3] = isReversed;
                      setCalibrators({ ...calibrators });
                      api.calibrate(name, min, true, isReversed);
                    }}
                  >
                    Reversed?
                  </Checkbox>
                  <Slider
                    range
                    reverse={isReversed}
                    value={[min, max]}
                    min={0}
                    max={255}
                    onChange={([newMin, newMax]) => {
                      const minChanged = newMin !== min;
                      calibrators[name][1] = newMin;
                      calibrators[name][2] = newMax;
                      setCalibrators({ ...calibrators });
                      api.calibrate(
                        name,
                        minChanged ? newMin : newMax,
                        minChanged,
                        isReversed
                      );
                    }}
                  />
                </div>
              )
            )}
          </CalibrationPanel>
        ) : (
          <>
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
                height="70vh"
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
                {/* <ConfigButtons>
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
            </ConfigButtons>
            <KickButton onClick={api.kick}>
              <b>KICK</b>
            </KickButton> */}
                <MenuButton onClick={() => setMenuOpen(true)}>MENU</MenuButton>
              </ButtonContainer>
            </RightSide>
          </>
        )}
      </Container>
      )}
      <Rodal
        visible={isMenuOpen}
        onClose={() => setMenuOpen(false)}
        width={550}
        height={300}
      >
        <h4>Actions</h4>
        <button onClick={() => api.do("thriller")}>Thriller Dance</button>
        <button onClick={() => api.do("default")}>Default</button>
        <button
          onClick={() => {
            api.beginCalibration().then(setCalibrators);
            setMenuOpen(false);
          }}
        >
          Enter Calibration
        </button>
      </Rodal>
    </App>
  ) : (
    <p>Creating a live connection to the robot...</p>
  );
