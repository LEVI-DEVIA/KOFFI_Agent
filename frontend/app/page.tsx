import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";

export default function YourApp() {
  return (
    <div className="h-screen w-screen bg-black">
      <CopilotChat
        labels={{
          title: "CopilotKit",
          initial: "Hi you! 👋 I can help you create a presentation on any topic.",
        }}
        className="h-full"
      />
    </div>
  );
}