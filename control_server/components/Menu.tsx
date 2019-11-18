import Rodal from "rodal";

import "rodal/lib/rodal.css";

import { API } from "../ts/api";

interface IMenuProps {
  onClose: () => void;
  api: API;
}

const Menu = ({ onClose, api }: IMenuProps) => (
  <Rodal visible={true} onClose={onClose} width={550} height={300}>
    <h4>Menu</h4>
    <button>Say hi to server</button>
  </Rodal>
);

export default Menu;
