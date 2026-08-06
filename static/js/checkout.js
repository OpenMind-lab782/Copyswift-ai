/*
 * CopySwiftAI Checkout
 */

async function checkout(plan, gateway = "paystack") {

    try {

        const result = await API.checkout(
            plan,
            gateway,
        );

        console.log(result);

        const payment =
            result.payment?.engine_response;

        if (
            payment &&
            payment.authorization_url
        ) {

            window.location.href =
                payment.authorization_url;

            return;
        }

        alert("Checkout session created successfully.");

    } catch (error) {

        console.error(error);

        alert("Unable to start checkout.");
    }

}

window.checkout = checkout;
