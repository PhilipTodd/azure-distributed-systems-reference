(function () {
  var tabsRoots = document.querySelectorAll("[data-tabs]");
  tabsRoots.forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('[role="tabpanel"]'));

    function activate(index, focus) {
      tabs.forEach(function (tab, i) {
        var selected = i === index;
        tab.setAttribute("aria-selected", selected ? "true" : "false");
        tab.tabIndex = selected ? 0 : -1;
        if (panels[i]) {
          panels[i].hidden = !selected;
        }
      });
      if (focus && tabs[index]) {
        tabs[index].focus();
      }
    }

    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () {
        activate(index, false);
      });
      tab.addEventListener("keydown", function (event) {
        var next = index;
        if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
        else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = tabs.length - 1;
        else return;
        event.preventDefault();
        activate(next, true);
      });
    });
  });

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      var value = button.getAttribute("data-copy") || "";
      var restore = button.textContent;
      function done() {
        button.textContent = "Copied";
        button.classList.add("is-copied");
        setTimeout(function () {
          button.textContent = restore;
          button.classList.remove("is-copied");
        }, 1500);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(done);
      } else {
        done();
      }
    });
  });

  var toggle = document.querySelector("[data-nav-toggle]");
  var backdrop = document.querySelector("[data-nav-backdrop]");

  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (backdrop) backdrop.hidden = !open;
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setNav(!document.body.classList.contains("nav-open"));
    });
  }
  if (backdrop) {
    backdrop.addEventListener("click", function () {
      setNav(false);
    });
  }
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !document.body.classList.contains("lightbox-open")) {
      setNav(false);
    }
  });

  var lightbox = document.querySelector("[data-lightbox-root]");
  var lightboxImage = lightbox && lightbox.querySelector("[data-lightbox-image]");
  var lightboxCaption = lightbox && lightbox.querySelector("[data-lightbox-caption]");
  var lightboxClose = lightbox && lightbox.querySelector(".lightbox__close");
  var lightboxTrigger = null;

  function closeLightbox() {
    if (!lightbox || lightbox.hidden) return;
    lightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
    if (lightboxImage) {
      lightboxImage.removeAttribute("src");
      lightboxImage.alt = "";
    }
    if (lightboxTrigger) {
      lightboxTrigger.focus();
      lightboxTrigger = null;
    }
  }

  function openLightbox(trigger) {
    if (!lightbox || !lightboxImage) return;
    var image = trigger.querySelector("img");
    var figure = trigger.closest("figure");
    var caption = figure && figure.querySelector("figcaption");
    var alt = image ? image.getAttribute("alt") || "" : "";
    var captionText = caption ? caption.textContent.trim() : alt;

    lightboxTrigger = trigger;
    lightboxImage.src = trigger.getAttribute("href") || (image && image.getAttribute("src")) || "";
    lightboxImage.alt = alt;
    if (lightboxCaption) {
      lightboxCaption.textContent = captionText;
      lightboxCaption.hidden = !captionText;
    }
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    if (lightboxClose) lightboxClose.focus();
  }

  document.querySelectorAll("[data-lightbox]").forEach(function (trigger) {
    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      openLightbox(trigger);
    });
  });

  if (lightbox) {
    lightbox.querySelectorAll("[data-lightbox-close]").forEach(function (control) {
      control.addEventListener("click", closeLightbox);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeLightbox();
      if (event.key !== "Tab" || lightbox.hidden || !lightboxClose) return;
      event.preventDefault();
      lightboxClose.focus();
    });
  }
})();
