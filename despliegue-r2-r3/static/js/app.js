// Mantener la página usable aun cuando JavaScript no está disponible.
document.querySelectorAll('[role="status"]').forEach(function (message) {
    message.setAttribute('tabindex', '-1');
    message.focus();
});
