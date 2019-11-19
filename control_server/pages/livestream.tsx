import dynamic from "next/dynamic";

const LiveStream = dynamic(
  async () => (await import("../components/LiveStream")).ManagedStream,
  { ssr: false }
);

export default () => <LiveStream />;
