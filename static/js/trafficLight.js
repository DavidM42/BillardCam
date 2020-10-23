
window.onload = () => {
    document.querySelectorAll('.traffic').forEach((e) => e.onclick = () => {
        window.location.reload(true);
    });
};