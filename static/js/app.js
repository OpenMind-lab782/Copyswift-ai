/*
 * CopySwiftAI Application Bootstrap
 */

async function initializeApplication() {

    console.log("==================================");
    console.log("CopySwiftAI");
    console.log("Version:", CopySwiftAI.version);
    console.log("==================================");

    try {

        const system = await API.system();

        console.log("Backend Status:", system.status);
        console.log("Platform:", system.platform.platform);

        const frontend = await API.frontend();

        console.log("Frontend Status:", frontend.status);

        console.log("Application Ready");

    } catch (error) {

        console.error(error);

        console.log("Application Offline");

    }

}

window.addEventListener(
    "load",
    initializeApplication,
);
