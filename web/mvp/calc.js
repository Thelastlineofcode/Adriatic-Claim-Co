// Minimal calculator + form handler for MVP intake
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("intake");
  const calcBtn = document.getElementById("calc");
  const out = document.getElementById("out");
  const summary = document.getElementById("summary");

  function compute(claimAmount, flatFee) {
    const texasContingency = 0.1; // Texas cap
    const contingencyFee =
      Math.round(claimAmount * texasContingency * 100) / 100;
    const contingencyNet =
      Math.round((claimAmount - contingencyFee) * 100) / 100;
    const flatFeeNum = flatFee ? Number(flatFee) : null;
    const flatNet = flatFeeNum
      ? Math.round((claimAmount - flatFeeNum) * 100) / 100
      : null;
    return { contingencyFee, contingencyNet, flatFee: flatFeeNum, flatNet };
  }

  calcBtn.addEventListener("click", function () {
    const claimAmount = Number(
      document.getElementById("claim_amount").value || 0
    );
    const flatFee = document.getElementById("flat_fee").value;
    if (!claimAmount || claimAmount <= 0) {
      alert("Enter a positive claim amount");
      return;
    }
    const res = compute(claimAmount, flatFee === "none" ? null : flatFee);
    out.hidden = false;
    let html = `<strong>Contingency (10%)</strong>: Fee $${res.contingencyFee.toFixed(2)}, You receive $${res.contingencyNet.toFixed(2)}<br/>`;
    if (res.flatNet !== null) {
      html += `<strong>Flat fee</strong>: Fee $${res.flatFee.toFixed(2)}, You receive $${res.flatNet.toFixed(2)}<br/>`;
      const best =
        res.flatNet > res.contingencyNet
          ? "Flat fee yields higher take-home"
          : "Contingency yields higher take-home";
      html += `<em>${best}</em>`;
    }
    summary.innerHTML = html;
  });

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    const data = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      phone: document.getElementById("phone").value,
      claim_amount: Number(document.getElementById("claim_amount").value || 0),
      flat_fee:
        document.getElementById("flat_fee").value === "none"
          ? null
          : Number(document.getElementById("flat_fee").value),
    };
    const res = compute(data.claim_amount, data.flat_fee);
    data.calculation = res;

    fetch("/api/claims", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((r) => r.json())
      .then((j) => {
        out.hidden = false;
        summary.innerHTML = `<strong>Submitted</strong><br/>Server net: $${j.net.toFixed(2)}<br/>Message: ${j.message}`;
      })
      .catch((err) => {
        alert("Submission failed: " + err.message);
      });
  });
});
