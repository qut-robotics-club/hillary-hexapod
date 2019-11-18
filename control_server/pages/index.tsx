import dynamic from "next/dynamic";

const Gamepad = dynamic(() => import("../components/Gamepad"), {
  ssr: false
});

export default () => (
  <>
    <Gamepad />
    <style jsx global>{`
      body {
        margin: 0;
      }
    `}</style>
  </>
);
