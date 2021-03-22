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

function getNewPrivateKey(privateKeyElementId) {
  const privateKeyElement = document.getElementById(privateKeyElementId);
  fetch('/get_new_private_key')
    .then(response => response.json())
    .then(data => {
      privateKeyElement.value = data.private_key_pem;
      privateKeyElement.dispatchEvent(new Event('change'));
    });
}

function getDnsRecord(selectorValue, privateKeyValue, dnsRecordElementId) {
  const dnsRecordElement = document.getElementById(dnsRecordElementId);
  fetch('/get_dkim_dns_record', {
    method: 'POST',
    body: JSON.stringify({
      selector: selectorValue,
      private_key_pem: privateKeyValue,
    }),
  })
    .then(response => response.json())
    .then(data => {
      dnsRecordElement.innerHTML = data.dns_record || '';
    });
}

function listenForSelectorOrPrivateKeyChange(selectorElementId, privateKeyElementId, dnsRecordElementId) {
  const selectorElement = document.getElementById(selectorElementId);
  const privateKeyElement = document.getElementById(privateKeyElementId);
  const updateDnsRecordFunction = function(event) {
    const selectorElement = document.getElementById(selectorElementId);
    const privateKeyElement = document.getElementById(privateKeyElementId);
    getDnsRecord(selectorElement.value, privateKeyElement.value, dnsRecordElementId);
  };
  selectorElement.addEventListener('change', updateDnsRecordFunction);
  privateKeyElement.addEventListener('change', updateDnsRecordFunction);
}
