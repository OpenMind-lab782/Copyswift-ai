/*
 * CopySwiftAI Home Page
 */

async function initializeHome() {

    try {

        const system = await API.system();

        console.log("Platform:", system.platform.name);
        console.log("Version:", system.platform.version);

        const frontend = await API.frontend();

        console.log("Frontend:", frontend);

        document.body.setAttribute(
            "data-platform-status",
            frontend.status,
        );

    } catch (error) {

        console.error(error);

        document.body.setAttribute(
            "data-platform-status",
            "offline",
        );
    }

}

window.addEventListener(
    "load",
    initializeHome,
);
