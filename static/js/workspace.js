/*
 * CopySwiftAI Unified Workspace
 */

class CopySwiftWorkspace {

    constructor() {
        this.ready = false;
    }

    async initialize() {

        console.log("Initializing CopySwiftAI Workspace...");

        try {

            const system = await API.system();

            this.ready = true;

            document.getElementById(
                "workspace-status"
            ).textContent = "Ready";

            document.getElementById(
                "workspace-platform"
            ).textContent =
                system.platform.platform;

            document.getElementById(
                "workspace-version"
            ).textContent =
                system.platform.version;

            console.log(
                "Workspace Ready:",
                system.platform.platform,
                system.platform.version
            );

        } catch (error) {

            console.error(error);

            this.ready = false;

        }

    }

    async askAssistant(message) {

        const customer =
            localStorage.getItem("copyswift_email") ||
            "Guest";

        return API.assistant(
            customer,
            "general",
            message,
        );

    }

    isReady() {
        return this.ready;
    }

    async customerDashboard() {
        return API.dashboard();
    }

    async customerProfile() {
        return API.profile();
    }

    async customerSummary() {

        const dashboard =
            await this.customerDashboard();

        const profile =
            await this.customerProfile();

        return {
            dashboard,
            profile,
        };

    }

    async checkout(plan, gateway = "paystack") {
        return API.checkout(plan, gateway);
    }

    async paymentHistory() {

        const dashboard =
            await this.customerDashboard();

        return dashboard.payments || [];

    }

    async subscription() {

        const dashboard =
            await this.customerDashboard();

        return (
            dashboard.subscription ||
            dashboard.customer ||
            {}
        );

    }

    async marketBrain(payload) {

        return API.marketBrain(
            payload,
        );

    }

    async marketStrategist(payload) {

        return API.marketStrategist(
            payload,
        );

    }

    async aiSalesManager(payload) {

        return API.aiSalesManager(
            payload,
        );

    }

}

window.Workspace = new CopySwiftWorkspace();

window.addEventListener(
    "load",
    () => Workspace.initialize(),
);
