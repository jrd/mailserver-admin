window.addEventListener('load', (event) => {
    initSidebarToggleEvent();
});

function initSidebarToggleEvent() {
    const body = document.body;
    const cssClassName = 'sidebar-visible';
    let glassPane;
    const navbtn = document.getElementById('navigation-toggler');
    const navbtn2 = document.getElementById('navigation-toggler2');
    const togglerFunction = function() {
        body.classList.toggle(cssClassName);
        if (body.classList.contains(cssClassName)) {
            glassPane = document.createElement('div');
            glassPane.classList.add('glass-pane', 'fade', 'show');
            glassPane.onclick = function() {
                body.classList.remove(cssClassName);
                body.removeChild(glassPane);
                glassPane = null;
            };
            body.appendChild(glassPane);
        } else {
            body.removeChild(glassPane);
            glassPane = null;
        }
    };
    if (navbtn) {
        navbtn.addEventListener('click', togglerFunction);
    }
    if (navbtn2) {
        navbtn2.addEventListener('click', togglerFunction);
    }
}
