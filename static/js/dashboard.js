/*
 * CopySwiftAI Dashboard
 */

async function loadDashboard() {

    try {

        const dashboard = await API.dashboard();

        console.log(dashboard);

        document.getElementById(
            "customer-name"
        ).textContent =
            dashboard.customer?.name || "Guest";

        document.getElementById(
            "customer-plan"
        ).textContent =
            dashboard.subscription?.plan ||
            dashboard.customer?.subscription ||
            "None";

        document.getElementById(
            "payment-count"
        ).textContent =
            dashboard.payment_count ??
            0;

    } catch (error) {

        console.error(error);

    }

}

window.addEventListener(
    "load",
    loadDashboard,
);
