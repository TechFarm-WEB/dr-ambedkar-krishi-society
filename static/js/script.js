// <!---------------------------------------------------------------------
// #  Author Modify    : Sakshi
// #  Creation Date    : 13/08/2026
// #  Transaction      : NA
// #  Application Area : Frontend Engine
// #  Object ID        : Neudocl
// #  BRF Application  : NA
// #  BRF DT           : NA
// #  ISSUE NO         : GIT HUB ISSUE NO
// #  Description      : Given Below
// # ------------------------------------------------------------------->

/* =====================================================================
   SOCIETY ARCHIVE — APP SCRIPT
   Mobile navigation, live dashboard stats, working document search,
   AJAX upload with on-screen confirmation, a real canvas-based scanner
   (brightness / contrast / sharpness + PNG/JPG/PDF export via jsPDF),
   a categories breakdown modal, and dynamic recent activity.
   No framework, no build step — talks to the Flask JSON APIs below:
     GET  /api/stats
     GET  /api/categories
     GET  /api/documents?q=&category=&date=
     GET  /api/activity
     POST /upload   (multipart: file[], category)
     POST /scan     (multipart: file, category)
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {
  /* -------------------------------------------------------------
     MOBILE / TABLET NAVIGATION DRAWER
     ------------------------------------------------------------- */
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebarOverlay");
  var menuBtn = document.getElementById("menuToggle");
  var closeBtn = document.getElementById("sidebarClose");
  var navLinks = document.querySelectorAll(".nav-link");

  function openSidebar() {
    sidebar.classList.add("is-open");
    overlay.classList.add("is-visible");
    menuBtn.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeSidebar() {
    sidebar.classList.remove("is-open");
    overlay.classList.remove("is-visible");
    menuBtn.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      if (sidebar.classList.contains("is-open")) closeSidebar();
      else openSidebar();
    });
  }
  if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && sidebar.classList.contains("is-open")) {
      closeSidebar();
      menuBtn.focus();
    }
  });

  function setActiveLink(link) {
    navLinks.forEach(function (l) {
      l.classList.remove("is-active");
    });
    link.classList.add("is-active");
  }

  navLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 1024px)").matches) closeSidebar();
      setActiveLink(link);
    });
  });

  var sections = [];
  navLinks.forEach(function (link) {
    var href = link.getAttribute("href") || "";
    if (href.charAt(0) === "#") {
      var section = document.getElementById(href.slice(1));
      if (section) sections.push({ link: link, section: section });
    }
  });

  if (sections.length) {
    var navObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var match = sections.find(function (s) {
              return s.section === entry.target;
            });
            if (match) setActiveLink(match.link);
          }
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0 },
    );
    sections.forEach(function (s) {
      navObserver.observe(s.section);
    });
  }

  /* -------------------------------------------------------------
     TOAST NOTIFICATIONS
     ------------------------------------------------------------- */
  var toastStack = document.getElementById("toastStack");

  function showToast(message, isError) {
    if (!toastStack) return;
    var toast = document.createElement("div");
    toast.className = "toast" + (isError ? " is-error" : "");
    toast.setAttribute("role", "status");

    var icon = document.createElement("i");
    icon.className = isError
      ? "fa-solid fa-circle-exclamation"
      : "fa-solid fa-circle-check";
    icon.setAttribute("aria-hidden", "true");

    var text = document.createElement("span");
    text.textContent = message;

    var closeBtnEl = document.createElement("button");
    closeBtnEl.type = "button";
    closeBtnEl.className = "toast-close";
    closeBtnEl.setAttribute("aria-label", "Dismiss notification");
    closeBtnEl.innerHTML =
      '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
    closeBtnEl.addEventListener("click", function () {
      toast.remove();
    });

    toast.appendChild(icon);
    toast.appendChild(text);
    toast.appendChild(closeBtnEl);
    toastStack.appendChild(toast);

    setTimeout(function () {
      toast.remove();
    }, 6000);
  }

  /* -------------------------------------------------------------
     SMALL HELPERS
     ------------------------------------------------------------- */
  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (ch) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[ch];
    });
  }

  // function formatDate(isoString) {
  //   var d = new Date(isoString);
  //   if (isNaN(d.getTime())) return isoString;
  //   return d.toLocaleDateString(undefined, {
  //     day: "2-digit",
  //     month: "short",
  //     year: "numeric",
  //   });
  // }

  /* -------------------------------------------------------------
   FORMAT DATE + TIME
   Example Output:
   22 Aug 2026, 03:45:21 PM
------------------------------------------------------------- */
function formatDate(isoString) {
  var d = new Date(isoString);

  if (isNaN(d.getTime())) {
    return isoString;
  }

  return d.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  });
}

  function animateCount(el, target) {
    if (!el) return;
    var start = 0;
    var duration = 600;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      el.textContent = Math.round(start + (target - start) * progress);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }

  /* -------------------------------------------------------------
   DASHBOARD STATS (Total Documents / Categories / New Uploads)
   ------------------------------------------------------------- */

var statTotal = document.getElementById("statTotalDocuments");
var statCategories = document.getElementById("statCategories");
var statNewUploads = document.getElementById("statNewUploads");

/* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Report section statistics
   ===================================================== */

var reportTotalDocuments = document.getElementById("reportTotalDocuments");
var reportTotalUsers = document.getElementById("reportTotalUsers");
var reportScannedDocuments = document.getElementById("reportScannedDocuments");
var reportUploadedDocuments = document.getElementById("reportUploadedDocuments");
var reportNewUploads = document.getElementById("reportNewUploads");
var reportCategories = document.getElementById("reportCategories");

function refreshStats() {

  fetch("/api/stats")

    .then(function (res) {

      return res.json();

    })

    .then(function (data) {

      animateCount(statTotal, data.total_documents || 0);
      animateCount(statCategories, data.categories || 0);
      animateCount(statNewUploads, data.new_uploads || 0);

      /* =====================================================
         ABHISHEK CHANGE
         Purpose:
         Populate Reports dashboard statistics
         ===================================================== */

      if (reportTotalDocuments)
        reportTotalDocuments.textContent = data.total_documents || 0;

      if (reportTotalUsers)
        reportTotalUsers.textContent = data.total_users || 0;

      if (reportScannedDocuments)
        reportScannedDocuments.textContent = data.scanned_documents || 0;

      if (reportUploadedDocuments)
        reportUploadedDocuments.textContent = data.uploaded_documents || 0;

      if (reportNewUploads)
        reportNewUploads.textContent = data.new_uploads || 0;

      if (reportCategories)
        reportCategories.textContent = data.categories || 0;

    })

    .catch(function () {

      /* stats are non-critical; fail quietly */

    });

}

  /* -------------------------------------------------------------
     CATEGORIES BREAKDOWN MODAL
     ------------------------------------------------------------- */
  var categoriesModal = document.getElementById("categoriesModal");
  var categoriesModalBody = document.getElementById("categoriesModalBody");
  var categoriesModalClose = document.getElementById("categoriesModalClose");
  var statCategoriesBtn = document.getElementById("statCategoriesBtn");
  var lastFocusedBeforeModal = null;

  function openCategoriesModal() {
    lastFocusedBeforeModal = document.activeElement;
    categoriesModal.classList.add("is-visible");
    categoriesModalBody.innerHTML = '<p class="list-empty">Loading…</p>';

    fetch("/api/categories")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data.length) {
          categoriesModalBody.innerHTML =
            '<p class="list-empty">No categories found.</p>';
          return;
        }
        categoriesModalBody.innerHTML = data
          .map(function (cat) {
            return (
              '<div class="modal-cat-row">' +
              '<span class="cat-label"><i class="fa-solid fa-folder" aria-hidden="true"></i>' +
              escapeHtml(cat.name) +
              "</span>" +
              '<span class="cat-count">' +
              cat.count +
              "</span>" +
              "</div>"
            );
          })
          .join("");
      })
      .catch(function () {
        categoriesModalBody.innerHTML =
          '<p class="list-empty">Could not load categories right now.</p>';
      });

    categoriesModalClose.focus();
  }

  function closeCategoriesModal() {
    categoriesModal.classList.remove("is-visible");
    if (lastFocusedBeforeModal) lastFocusedBeforeModal.focus();
  }

  if (statCategoriesBtn)
    statCategoriesBtn.addEventListener("click", openCategoriesModal);
  if (categoriesModalClose)
    categoriesModalClose.addEventListener("click", closeCategoriesModal);
  if (categoriesModal) {
    categoriesModal.addEventListener("click", function (e) {
      if (e.target === categoriesModal) closeCategoriesModal();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && categoriesModal.classList.contains("is-visible"))
      closeCategoriesModal();
  });

  /* -------------------------------------------------------------
     DOCUMENT TABLE / SEARCH
     ------------------------------------------------------------- */
  var tableBody = document.getElementById("documentsTableBody");
  var cardList = document.getElementById("documentsCardList");
  var searchForm = document.getElementById("searchForm");
  var searchResultInfo = document.getElementById("searchResultInfo");

 function renderDocuments(docs) {


    if (!docs.length) {
      tableBody.innerHTML =
        '<tr class="state-row"><td colspan="7">' +
        '<i class="fa-regular fa-folder-open" aria-hidden="true"></i>&nbsp; No documents found.</td></tr>';
      cardList.innerHTML = '<p class="list-empty">No documents found.</p>';
      return;
    }

    tableBody.innerHTML = docs
      .map(function (doc) {
        return (
  "<tr>" +

  '<td><input type="checkbox" class="doc-checkbox" value="' +
  doc.id +
  '"></td>' +

  "<td>" +
  escapeHtml(doc.filename) +
  "</td>" +
          "<td>" +
          escapeHtml(doc.category) +
          "</td>" +
          /* Display upload date and exact time */
          "<td>" +
escapeHtml(doc.uploaded_by || "Unknown") +
"</td>" +

"<td>" +
formatDate(doc.uploaded_at) +
"</td>" +
          '<td><span class="status">Active</span></td>' +
          /* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Enable document download from dashboard
   ===================================================== */
   /* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Enable document preview from dashboard
   ===================================================== */

'<td>' +

'<a href="/preview/' +
doc.id +
'" class="btn btn-outline">👁 Preview</a> ' +

'<a href="/download/' +
doc.id +
'" class="btn btn-outline">Download</a>' +

/* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Show Delete button only for admin users
   ===================================================== */

(USER_ROLE === "admin"
    ? ' <a href="/delete/' +
      doc.id +
      '" class="btn btn-outline" onclick="return confirm(\'Delete this document?\')">Delete</a>'
    : '') +

'</td>' +
          "</tr>"
        );
      })
      .join("");

    cardList.innerHTML = docs
      .map(function (doc) {
        return (
          '<div class="doc-card">' +
          '<div class="doc-name">' +
          escapeHtml(doc.filename) +
          "</div>" +
          '<div class="doc-meta">' +
          '<span><i class="fa-solid fa-layer-group" aria-hidden="true"></i>' +
          escapeHtml(doc.category) +
          "</span>" +
          /* Mobile card date + time */
          '<span><i class="fa-regular fa-calendar" aria-hidden="true"></i>' +
          formatDate(doc.uploaded_at) +
          "</span>" +
          '<span class="status">Active</span>' +
          "</div>" +
          /* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Enable document download on mobile cards
   ===================================================== */

'<a href="/preview/' +
doc.id +
'" class="btn btn-outline btn-block">👁 Preview</a>' +

'<a href="/download/' +
doc.id +
'" class="btn btn-outline btn-block">Download</a>' +

/* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Show Delete button on mobile cards for admin users
   ===================================================== */
   /* =====================================================
   ABHISHEK CHANGE
   Purpose:
   Enable document preview on mobile cards
   ===================================================== */

'<a href="/preview/' +
doc.id +
'" class="btn btn-outline btn-block">👁 Preview</a>' +

(USER_ROLE === "admin"
    ? '<a href="/delete/' +
      doc.id +
      '" class="btn btn-outline btn-block" onclick="return confirm(\'Delete this document?\')">Delete</a>'
    : '') +
          "</div>"
        );
      })
      .join("");
  }

  function loadDocuments(params) {

  

    var query = new URLSearchParams();

    if (params) {
        if (params.q) query.set("q", params.q);
        if (params.category) query.set("category", params.category);
        if (params.date) query.set("date", params.date);
    }

    tableBody.innerHTML =
        '<tr class="state-row"><td colspan="6">Loading documents...</td></tr>';

    cardList.innerHTML =
        '<p class="list-empty">Loading documents...</p>';

    tableBody.innerHTML =
      '<tr class="state-row"><td colspan="6">Loading documents…</td></tr>';
    cardList.innerHTML = '<p class="list-empty">Loading documents…</p>';

    fetch("/api/documents?" + query.toString())
      .then(function (res) {
        return res.json();
      })
      .then(function (docs) {
        renderDocuments(docs);
        if (searchResultInfo) {
          var hasFilter =
            params && (params.q || params.category || params.date);
          searchResultInfo.textContent = hasFilter
            ? docs.length + " result(s) found."
            : "";
        }
      })
      .catch(function () {
        tableBody.innerHTML =
          '<tr class="state-row"><td colspan="6">Could not load documents right now.</td></tr>';
        cardList.innerHTML =
          '<p class="list-empty">Could not load documents right now.</p>';
      });
  }

  // if (searchForm) {
  //   searchForm.addEventListener("submit", function (e) {
  //     e.preventDefault();
  //     var formData = new FormData(searchForm);
  //     loadDocuments({
  //       q: formData.get("q"),
  //       category: formData.get("category"),
  //       date: formData.get("date"),
  //     });
  //   });
  // }
  if (searchForm) {

  searchForm.addEventListener("submit", function (e) {

    e.preventDefault();
    // alert("SEARCH CLICKED");

    var formData = new FormData(searchForm);

    fetch(
      "/api/documents?q=" +
      encodeURIComponent(formData.get("q") || "") +
      "&category=" +
      encodeURIComponent(formData.get("category") || "") +
      "&date=" +
      encodeURIComponent(formData.get("date") || "")
    )

    .then(function (res) {
      return res.json();
    })

    .then(function (docs) {
      
      // alert("DOCS RECEIVED = " + docs.length);
      // alert("OPENING MODAL");
      categoryDocumentsModal.classList.add("is-visible");

      document.getElementById(
        "categoryDocumentsTitle"
      ).textContent = "Search Results";

      if (!docs.length) {

        categoryDocumentsBody.innerHTML =
          "<p class='list-empty'>No documents found.</p>";

        return;
      }

      categoryDocumentsBody.innerHTML =

      '<div class="table-scroll">' +
      '<table>' +
      '<thead>' +
      '<tr>' +
      '<th>Document</th>' +
      '<th>Uploaded By</th>' +
      '<th>Date</th>' +
      '<th>Action</th>' +
      '</tr>' +
      '</thead>' +
      '<tbody>' +

      docs.map(function(doc){

        return (

          '<tr>' +

          '<td>' +
          escapeHtml(doc.filename) +
          '</td>' +

          '<td>' +
          escapeHtml(doc.uploaded_by || "Unknown") +
          '</td>' +

          '<td>' +
          formatDate(doc.uploaded_at) +
          '</td>' +

          '<td>' +
          '<a href="/preview/' +
          doc.id +
          '" class="btn btn-outline">👁 Preview</a> ' +
          '<a href="/download/' +
          doc.id +
          '" class="btn btn-outline">Download</a>' +
          (USER_ROLE === "admin"
            ? ' <a href="/delete/' +
              doc.id +
              '" class="btn btn-outline" onclick="return confirm(\'Delete this document?\')">Delete</a>'
            : '') +
          '</td>' +

          '</tr>'

        );

      }).join("") +

      '</tbody>' +
      '</table>' +
      '</div>';

    });

  });

}
console.log("SEARCH BLOCK LOADED");

  /* -------------------------------------------------------------
     RECENT ACTIVITY
     ------------------------------------------------------------- */
  var activityTableBody = document.getElementById("activityTableBody");
  var activityCardList = document.getElementById("activityCardList");
//   
var activityModal =
  document.getElementById("activityModal");

var openActivityModal =
  document.getElementById("openActivityModal");

var closeActivityModal =
  document.getElementById("closeActivityModal");

var activityModalList =
  document.getElementById("activityModalList");


if (openActivityModal && activityModal) {

  openActivityModal.addEventListener(
    "click",
    function () {

      activityModal.classList.add("is-visible");

    }
  );

}


if (closeActivityModal && activityModal) {

  closeActivityModal.addEventListener(
    "click",
    function () {

      activityModal.classList.remove("is-visible");

    }
  );

}


/* Close popup when clicking outside */

if (activityModal) {

  activityModal.addEventListener(
    "click",
    function (e) {

      if (e.target === activityModal) {

        activityModal.classList.remove("is-visible");

      }

    }
  );

}



  function renderActivity(items) {
    if (!items.length) {
      activityTableBody.innerHTML =
        '<tr class="state-row"><td colspan="3">No activity yet.</td></tr>';
      activityCardList.innerHTML = '<p class="list-empty">No activity yet.</p>';
      return;
    }

    activityTableBody.innerHTML = items
      .map(function (item) {
        return (
          "<tr>" +
          "<td>" +
          escapeHtml(item.user) +
          "</td>" +
          "<td>" +
          escapeHtml(item.action) +
          "</td>" +
          /* Display activity date and exact time */
          "<td>" +
          formatDate(item.date) +
          "</td>" +
          "</tr>"
        );
      })
      .join("");

    /* Recent Activity Popup Data */

if (activityModalList) {

  activityModalList.innerHTML = items
    .map(function (item) {

      var icon =
        item.source === "scanner"
          ? "fa-print"
          : "fa-cloud-arrow-up";

      return (
        '<div class="activity-row">' +

          '<div class="activity-icon">' +
            '<i class="fa-solid ' + icon + '"></i>' +
          '</div>' +

          '<div class="activity-text">' +

            '<div class="who">' +
              escapeHtml(item.user) +
            '</div>' +

            '<div>' +
              escapeHtml(item.action) +
            '</div>' +

            '<div class="activity-date">' +
              formatDate(item.date) +
            '</div>' +

          '</div>' +

        '</div>'
      );

    })
    .join("");

}

    activityCardList.innerHTML = items
      .map(function (item) {
        var icon = item.source === "scanner" ? "fa-print" : "fa-cloud-arrow-up";
        return (
          '<div class="activity-row">' +
          '<div class="activity-icon" aria-hidden="true"><i class="fa-solid ' +
          icon +
          '"></i></div>' +
          '<div class="activity-text"><span class="who">' +
          escapeHtml(item.user) +
          "</span> " +
          escapeHtml(item.action) +
          '<div class="activity-date">' +
          formatDate(item.date) +
          "</div></div>" +
          "</div>"
        );
      })
      .join("");
  }

  function refreshActivity() {
    fetch("/api/activity?limit=8")
      .then(function (res) {
        return res.json();
      })
      .then(renderActivity)
      .catch(function () {
        activityTableBody.innerHTML =
          '<tr class="state-row"><td colspan="3">Could not load activity right now.</td></tr>';
        activityCardList.innerHTML =
          '<p class="list-empty">Could not load activity right now.</p>';
      });
  }

  /* -------------------------------------------------------------
     GLOBAL REFRESH — after any successful upload or scan save
     ------------------------------------------------------------- */
  function refreshEverything() {
    refreshStats();
    refreshActivity();
    loadDocuments(null);
  }

  /* -------------------------------------------------------------
     UPLOAD — DRAG & DROP + AJAX SUBMIT WITH CONFIRMATION
     ------------------------------------------------------------- */
  var dropzone = document.getElementById("dropzone");
  var fileInput = document.getElementById("file");
  var fileList = document.getElementById("fileList");
  var uploadForm = document.getElementById("uploadForm");
  var uploadSubmitBtn = document.getElementById("uploadSubmitBtn");

  function renderFileList(files) {
    if (!fileList) return;
    fileList.innerHTML = "";
    if (!files || !files.length) return;
    Array.prototype.forEach.call(files, function (file) {
      var li = document.createElement("li");
      li.innerHTML =
        '<i class="fa-regular fa-file" aria-hidden="true"></i><span>' +
        escapeHtml(file.name) +
        "</span>";
      fileList.appendChild(li);
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      renderFileList(fileInput.files);
    });
  }

  if (dropzone && fileInput) {
    ["dragenter", "dragover"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        dropzone.classList.add("is-dragover");
      });
    });
    ["dragleave", "drop"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        dropzone.classList.remove("is-dragover");
      });
    });
    dropzone.addEventListener("drop", function (e) {
      var dropped = e.dataTransfer && e.dataTransfer.files;
      if (dropped && dropped.length) {
        fileInput.files = dropped;
        renderFileList(dropped);
      }
    });
  }

  if (uploadForm) {
    uploadForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var formData = new FormData(uploadForm);
      uploadSubmitBtn.disabled = true;
      uploadSubmitBtn.textContent = "Uploading…";

      fetch("/upload", {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          if (result.ok && result.data.success) {
            showToast(result.data.message, false);
            uploadForm.reset();
            renderFileList([]);
            // refreshEverything();
          } else {
            showToast(
              result.data.message || "Upload failed. Please try again.",
              true,
            );
          }
        })
        .catch(function () {
          showToast(
            "Upload failed. Please check your connection and try again.",
            true,
          );
        })
        .finally(function () {
          uploadSubmitBtn.disabled = false;
          uploadSubmitBtn.innerHTML =
            '<i class="fa-solid fa-cloud-arrow-up" aria-hidden="true"></i> Upload Documents';
        });
    });
  }

  /* -------------------------------------------------------------
     SCANNER — LIVE CANVAS PREVIEW + REAL FILTERING + SAVE
     ------------------------------------------------------------- */
  var scanFileInput = document.getElementById("scan-file");
  var scanCategorySelect = document.getElementById("scan-category");
  var scannerPreview = document.getElementById("scannerPreview");
  var brightnessRange = document.getElementById("brightness");
  var contrastRange = document.getElementById("contrast");
  var sharpnessRange = document.getElementById("sharpness");
  var outputFormatSelect = document.getElementById("output-format");
  var scanGenerateBtn = document.getElementById("scanGenerateBtn");
  var scanSaveBtn = document.getElementById("scanSaveBtn");
  var scannerStatus = document.getElementById("scannerStatus");

  var sourceImage = null;
  var scannerCanvas = null;
  var scannerCtx = null;
  var scanGenerated = false;

  document
    .querySelectorAll('.range-row input[type="range"]')
    .forEach(function (range) {
      var out = range.parentElement.querySelector(".range-value");
      if (out) {
        out.textContent = range.value + "%";
        range.addEventListener("input", function () {
          out.textContent = range.value + "%";
        });
      }
    });

  function ensureCanvas() {
    if (scannerCanvas) return;
    scannerCanvas = document.createElement("canvas");
    scannerCtx = scannerCanvas.getContext("2d");
    scannerPreview.innerHTML = "";
    scannerPreview.classList.add("has-image");
    scannerPreview.appendChild(scannerCanvas);
  }

  // Simple, real 3x3 convolution sharpen (unsharp-style), strength driven by the slider
  function applySharpen(ctx, width, height, amount) {
    if (amount <= 0) return;
    var weight = amount / 100; // 0..1
    var imageData = ctx.getImageData(0, 0, width, height);
    var src = imageData.data;
    var copy = new Uint8ClampedArray(src);

    var kernel = [0, -1, 0, -1, 5, -1, 0, -1, 0];

    for (var y = 1; y < height - 1; y++) {
      for (var x = 1; x < width - 1; x++) {
        for (var c = 0; c < 3; c++) {
          var i = (y * width + x) * 4 + c;
          var sum = 0;
          var k = 0;
          for (var ky = -1; ky <= 1; ky++) {
            for (var kx = -1; kx <= 1; kx++) {
              var idx = ((y + ky) * width + (x + kx)) * 4 + c;
              sum += copy[idx] * kernel[k];
              k++;
            }
          }
          src[i] = copy[i] * (1 - weight) + sum * weight;
        }
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

  function drawPreview() {
    if (!sourceImage) return;

    ensureCanvas();

    var maxWidth = 640;
    var scale = Math.min(1, maxWidth / sourceImage.width);
    scannerCanvas.width = Math.round(sourceImage.width * scale);
    scannerCanvas.height = Math.round(sourceImage.height * scale);

    var brightness = brightnessRange.value;
    var contrast = contrastRange.value;
    var sharpness = parseInt(sharpnessRange.value, 10);

    var brightnessPct = 50 + Number(brightness); // 50%..150%
    var contrastPct = 50 + Number(contrast); // 50%..150%

    scannerCtx.filter =
      "brightness(" + brightnessPct + "%) contrast(" + contrastPct + "%)";
    scannerCtx.drawImage(
      sourceImage,
      0,
      0,
      scannerCanvas.width,
      scannerCanvas.height,
    );
    scannerCtx.filter = "none";

    applySharpen(
      scannerCtx,
      scannerCanvas.width,
      scannerCanvas.height,
      sharpness,
    );
  }

  if (scanFileInput) {
    scanFileInput.addEventListener("change", function () {
      var file = scanFileInput.files && scanFileInput.files[0];
      if (!file) return;

      var reader = new FileReader();
      reader.onload = function (evt) {
        var img = new Image();
        img.onload = function () {
          sourceImage = img;
          scanGenerated = false;
          scanSaveBtn.disabled = true;
          scanGenerateBtn.disabled = false;
          scannerStatus.textContent =
            'Image loaded. Adjust the sliders, then click "Scan & Generate".';
          drawPreview();
        };
        img.src = evt.target.result;
      };
      reader.readAsDataURL(file);
    });
  }

  [brightnessRange, contrastRange, sharpnessRange].forEach(function (range) {
    if (!range) return;
    range.addEventListener("input", function () {
      if (sourceImage) drawPreview();
    });
  });

  if (scanGenerateBtn) {
    scanGenerateBtn.addEventListener("click", function () {
      if (!sourceImage) return;
      drawPreview();
      scanGenerated = true;
      scanSaveBtn.disabled = false;
      scannerStatus.textContent =
        'Scan ready. Choose a category and click "Save to Archive".';
    });
  }

  function canvasToBlob(format) {
    return new Promise(function (resolve, reject) {
      if (format === "pdf") {
        try {
          var jsPDFCtor = window.jspdf && window.jspdf.jsPDF;
          if (!jsPDFCtor) throw new Error("jsPDF not available");
          var orientation =
            scannerCanvas.width >= scannerCanvas.height ? "l" : "p";
          var pdf = new jsPDFCtor({
            orientation: orientation,
            unit: "px",
            format: [scannerCanvas.width, scannerCanvas.height],
          });
          var imgData = scannerCanvas.toDataURL("image/jpeg", 0.92);
          pdf.addImage(
            imgData,
            "JPEG",
            0,
            0,
            scannerCanvas.width,
            scannerCanvas.height,
          );
          resolve(pdf.output("blob"));
        } catch (err) {
          reject(err);
        }
        return;
      }

      var mime = format === "jpg" ? "image/jpeg" : "image/png";
      scannerCanvas.toBlob(
        function (blob) {
          if (blob) resolve(blob);
          else reject(new Error("Could not export image"));
        },
        mime,
        0.92,
      );
    });
  }

  if (scanSaveBtn) {
    scanSaveBtn.addEventListener("click", function () {
      if (!scanGenerated || !scannerCanvas) return;

      var format = outputFormatSelect.value;
      var category = scanCategorySelect.value;

      scanSaveBtn.disabled = true;
      scanSaveBtn.textContent = "Saving…";

      canvasToBlob(format)
        .then(function (blob) {
          var ext = format === "jpg" ? "jpg" : format === "pdf" ? "pdf" : "png";
          var filename = "scan_" + Date.now() + "." + ext;

          var formData = new FormData();
          formData.append("file", blob, filename);
          formData.append("category", category);

          return fetch("/scan", { method: "POST", body: formData }).then(
            function (res) {
              return res.json().then(function (data) {
                return { ok: res.ok, data: data };
              });
            },
          );
        })
        .then(function (result) {
          if (result.ok && result.data.success) {
            showToast(result.data.message, false);
            scannerStatus.textContent =
              "Saved. Select a new image to scan another document.";
            sourceImage = null;
            scanGenerated = false;
            scannerPreview.classList.remove("has-image");
            scannerPreview.innerHTML =
              '<i class="fa-regular fa-image" aria-hidden="true"></i>' +
              "<strong>Scanner Preview Area</strong>" +
              "<span>Choose an image below to see it here</span>";
            scanFileInput.value = "";
            scanGenerateBtn.disabled = true;
            refreshEverything();
          } else {
            showToast(result.data.message || "Could not save the scan.", true);
          }
        })
        .catch(function () {
          showToast("Could not save the scan. Please try again.", true);
        })
        .finally(function () {
          scanSaveBtn.disabled = false;
          scanSaveBtn.innerHTML =
            '<i class="fa-regular fa-floppy-disk" aria-hidden="true"></i> Save to Archive';
        });
    });
  }
/* -------------------------------------------------------------
   CATEGORY DOCUMENTS MODAL
   added by gaurav on 28/08/2026
------------------------------------------------------------- */

var categoryDocumentsModal =
  document.getElementById("categoryDocumentsModal");

var categoryDocumentsBody =
  document.getElementById("categoryDocumentsBody");

var categoryDocumentsClose =
  document.getElementById("categoryDocumentsClose");

var categoryTriggers =
  document.querySelectorAll(".category-modal-trigger");

function closeCategoryDocumentsModal() {
  categoryDocumentsModal.classList.remove("is-visible");
}

if (categoryDocumentsClose) {
  categoryDocumentsClose.addEventListener(
    "click",
    closeCategoryDocumentsModal
  );
}

if (categoryDocumentsModal) {
  categoryDocumentsModal.addEventListener(
    "click",
    function (e) {
      if (e.target === categoryDocumentsModal) {
        closeCategoryDocumentsModal();
      }
    }
  );
}

categoryTriggers.forEach(function (card) {

  card.addEventListener("click", function () {

    var category =
      card.getAttribute("data-category");

    document.getElementById(
      "categoryDocumentsTitle"
    ).textContent =
      category + " Documents";

    categoryDocumentsModal.classList.add(
      "is-visible"
    );

    categoryDocumentsBody.innerHTML =
      "<p>Loading documents...</p>";

    fetch(
      "/api/documents?category=" +
      encodeURIComponent(category)
    )

      .then(function (res) {
        return res.json();
      })

      .then(function (docs) {

        if (!docs.length) {

          categoryDocumentsBody.innerHTML =
            "<p class='list-empty'>No documents found in this category.</p>";

          return;
        }

        categoryDocumentsBody.innerHTML =

          '<div class="table-scroll">' +
          '<table>' +
          '<thead>' +
          '<tr>' +
          '<th>Document</th>' +
          '<th>Uploaded By</th>' +
          '<th>Date</th>' +
          '<th>Action</th>' +
          '</tr>' +
          '</thead>' +
          '<tbody>' +

          docs.map(function (doc) {

            return (

              '<tr>' +

              '<td>' +
              escapeHtml(doc.filename) +
              '</td>' +

              '<td>' +
              escapeHtml(doc.uploaded_by || "Unknown") +
              '</td>' +

              '<td>' +
              formatDate(doc.uploaded_at) +
              '</td>' +

             '<td>' +
    '<a href="/preview/' + doc.id + '">👁 Preview</a> ' +
    '<a href="/download/' + doc.id + '">Download</a>' +
'</td>' +

              '</tr>'

            );

          }).join("") +

          '</tbody>' +
          '</table>' +
          '</div>';

      })

      .catch(function () {

        categoryDocumentsBody.innerHTML =
          "<p class='list-empty'>Unable to load documents.</p>";

      });

  });

});

var addCategoryBtn =
document.getElementById("addCategoryBtn");

var addCategoryModal =
document.getElementById("addCategoryModal");

var addCategoryClose =
document.getElementById("addCategoryClose");

if(addCategoryBtn){

  addCategoryBtn.addEventListener(
    "click",
    function(){

      addCategoryModal.classList.add(
        "is-visible"
      );

    }
  );

}

if(addCategoryClose){

  addCategoryClose.addEventListener(
    "click",
    function(){

      addCategoryModal.classList.remove(
        "is-visible"
      );

    }
  );

}
var saveCategoryBtn =
document.getElementById("saveCategoryBtn");

if(saveCategoryBtn){

    saveCategoryBtn.addEventListener(
        "click",
        function(){

           var categoryName =
document.getElementById(
    "newCategoryName"
).value.trim();


if(!categoryName){

    alert("Please enter category name");

    return;
}



fetch("/api/category/create", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({

        category: categoryName

    })

})

.then(function(res){

    return res.json();

})

.then(function(data){
if(data.success){

    alert("Category Created Successfully");

    document.getElementById(
        "newCategoryName"
    ).value = "";

    addCategoryModal.classList.remove(
        "is-visible"
    );
    location.reload();

}

    else{

        alert(
            data.message ||
            "Unable to create category"
        );

    }

})
.catch(function(){

    alert("Server Error");

});


        }
    );

}

document.addEventListener(
    "click",
    function(event){

        const deleteBtn =
            event.target.closest(
                ".delete-category-btn"
            );

        if(deleteBtn){

            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();

            const categoryName =
                deleteBtn.dataset.category;

           if(
    confirm(
    "⚠ WARNING\n\n" +
    "Deleting this category cannot be undone.\n\n" +
    "The following data will be permanently removed:\n\n" +
    "• Category\n" +
    "• All files inside the category\n" +
    "• All document records\n\n" +
    "Category: " + categoryName +
    "\n\nProceed with deletion?"
)
){

    fetch(
        "/api/category/delete",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                category: categoryName
            })
        }
    )

    .then(function(response){

        return response.json();

    })

    .then(function(data){

        alert(data.message);

        if(data.success){

            location.reload();

        }

    })

    .catch(function(){

        alert(
            "Delete Failed"
        );

    });

}

            return false;

        }

    },
    true
);



var archiveOverviewBtns =
document.querySelectorAll(
    ".archiveOverviewBtn"
);

var archiveModal =
document.getElementById(
    "archiveModal"
);

var archiveModalClose =
document.getElementById(
    "archiveModalClose"
);

archiveOverviewBtns.forEach(function(btn){

    btn.addEventListener(
        "click",
        function(){

            if(!archiveModal){
                return;
            }

            archiveModal.classList.add(
                "is-visible"
            );

            var archiveBody =
                document.getElementById(
                    "archiveDocumentsBody"
                );

            if(archiveBody){
                archiveBody.innerHTML =
                    "<p class='list-empty'>Loading archive...</p>";
            }

            fetch("/api/archive")

            .then(function(res){

                return res.json();

            })

            .then(function(docs){

                if(!archiveBody){
                    return;
                }

                if(!docs.length){

                    archiveBody.innerHTML =
                        "<p class='list-empty'>No archived documents found.</p>";

                    return;
                }

                archiveBody.innerHTML =
                    docs.map(function(doc){

                        return `
                            <div class="file-row">

                                <div class="file-name">

                                    <strong>${doc.filename}</strong>

                                    <br>

                                    ${doc.category}

                                    <br>

                                    ${doc.document_date || ''}

                                </div>

                            </div>
                        `;

                    }).join("");

            })

            .catch(function(){

                if(archiveBody){

                    archiveBody.innerHTML =
                        "<p class='list-empty'>Unable to load archive.</p>";

                }

            });

        }
    );

});

if(
    archiveModalClose &&
    archiveModal
){

    archiveModalClose.addEventListener(
        "click",
        function(){

            archiveModal.classList.remove(
                "is-visible"
            );

        }
    );

}
  /* -------------------------------------------------------------
     INITIAL LOAD
     ------------------------------------------------------------- */
  refreshStats();
  refreshActivity();

});

  