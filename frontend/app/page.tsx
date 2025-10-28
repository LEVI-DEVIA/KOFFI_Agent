import "@copilotkit/react-ui/styles.css";
import { CopilotSidebar } from "@copilotkit/react-ui";

export default function YourApp() {
return (
    <main>
    <h1>Your main content</h1>
    <CopilotSidebar
        labels={{
            title: "Popup Assistant",
            initial: "Hi! I'm connected to an agent. How can I help?",
        }}
    />
    </main>
);
}