import { createRef, useEffect } from "react";

const drawRect = (ref: any = createRef()) =>
  (useEffect(() => {
    const ctx: CanvasRenderingContext2D = ref.current.getContext("2d");
    ctx.beginPath();
    ctx.fillRect(20, 20, 150, 100);
  }) as null) || ref;

const Test = ({ ref = drawRect() }: { ref: any }) => (
  <div>
    <canvas ref={ref}></canvas>
  </div>
);

export default Test;
