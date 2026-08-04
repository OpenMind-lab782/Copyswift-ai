/*
 * CopySwiftAI API Client
 */

class CopySwiftAPI {

    async get(url) {

        const response = await fetch(url);

        return await response.json();
    }

    async post(url, data) {

        const response = await fetch(url, {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify(data),
        });

        return await response.json();
    }

    system() {
        return this.get(CopySwiftAI.api.system);
    }

    frontend() {
        return this.get(CopySwiftAI.api.frontend);
    }

    login(email) {
        return this.post(
            CopySwiftAI.api.login,
            { email }
        );
    }

    logout(token) {
        return this.post(
            CopySwiftAI.api.logout,
            { token }
        );
    }

    assistant(customer, intent, message) {

        return this.post(
            CopySwiftAI.api.assistant,
            {
                customer,
                intent,
                message,
            }
        );
    }

    checkout(plan, gateway) {

        return this.post(
            CopySwiftAI.api.checkout,
            {
                plan,
                gateway,
            }
        );
    }

    dashboard() {
        return this.get(CopySwiftAI.api.dashboard);
    }

    profile() {
        return this.get(CopySwiftAI.api.profile);
    }


    adCopyGenerate(payload) {
        return this.post(
            "/tools/ad-copy/generate",
            payload,
        );
    }

    scrapeProductUrl(url) {
        return this.post(
            "/tools/ad-copy/scrape-url",
            { url },
        );
    }

    unlockBonus(email) {
        return this.post(
            "/tools/ad-copy/unlock-bonus",
            { email },
        );
    }



    marketBrain(payload) {
        return this.post(
            "/api/v1/market-brain",
            payload,
        );
    }

    marketStrategist(payload) {
        return this.post(
            "/api/v1/market-strategist",
            payload,
        );
    }

    aiSalesManager(payload) {
        return this.post(
            "/api/v1/ai-sales-manager",
            payload,
        );
    }
}

window.API = new CopySwiftAPI();
