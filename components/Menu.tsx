import Rodal from "rodal";

import "rodal/lib/rodal.css";

import { Api } from "../ts/api";

export default ({ onClose, api }: { onClose: () => void; api: Api }) => (
  <Rodal visible={true} onClose={onClose} width={550} height={300}>
    <h4>Actions</h4>
    <button onClick={() => api.do("thriller")}>Thriller Dance</button>
    <button onClick={() => api.do("default")}>Default</button>
    <button onClick={() => api.do("walk")}>Walk</button>
    <button onClick={() => api.do("rotate")}>Rotate</button>

    <h4>Calibration</h4>
    <button onClick={() => api.do("rotate")}>Enter Calibration</button>
  </Rodal>
);
