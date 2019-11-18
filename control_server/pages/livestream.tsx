import dynamic from "next/dynamic";

const LiveStream = dynamic(
  async () => {
    const { ManagedStream } = await import("../components/LiveStream");
    return ManagedStream;
  },
  {
    ssr: false
  }
);

export default () => <LiveStream />;
