

document.addEventListener('DOMContentLoaded', function () {
  initNavToggle();
  initFooterYear();

  if (document.getElementById('featuredArtifacts')) initHomePage();
  if (document.getElementById('catalogGrid')) initCatalogPage();
  if (document.getElementById('artifactDetail')) initDetailsPage();
  if (document.getElementById('overviewCards')) initDashboardAuthThenLoad();
  if (document.getElementById('loansTableBody')) initLoansPage();
});


async function initDashboardAuthThenLoad() {
  var pill = document.getElementById('backendPill');
  var gate = document.getElementById('loginGate');
  var online = (typeof ApiClient !== 'undefined') ? await ApiClient.isBackendOnline() : false;

  if (pill) {
    pill.textContent = online ? 'backend connected · MongoDB' : 'offline mode · sample data';
    pill.className = 'backend-pill ' + (online ? 'online' : 'offline');
  }

  if (online && !ApiClient.isLoggedIn) {
    gate.classList.add('show');
    wireLoginForm();
  } else {
    initDashboardPage();
    if (online) {
      applyLoggedInCurator();
      loadLiveDashboardData();
    }
  }

  var logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    if (!online) logoutBtn.style.display = 'none';
    logoutBtn.addEventListener('click', async function () {
      await ApiClient.logout();
      window.location.reload();
    });
  }
}

function wireLoginForm() {
  var form = document.getElementById('loginForm');
  var errorBox = document.getElementById('loginError');
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    errorBox.classList.remove('show');
    var email = document.getElementById('loginEmail').value.trim();
    var password = document.getElementById('loginPassword').value;
    try {
      await ApiClient.login(email, password);
      document.getElementById('loginGate').classList.remove('show');
      initDashboardPage();
      applyLoggedInCurator();
      loadLiveDashboardData();
    } catch (err) {
      errorBox.textContent = err.message || 'Login failed. Check your credentials.';
      errorBox.classList.add('show');
    }
  });
}

function applyLoggedInCurator() {
  var curator = ApiClient.curator;
  if (!curator) return;
  var initials = curator.name.split(' ').map(function (n) { return n[0]; }).join('').slice(0, 2).toUpperCase();
  var nameEl = document.getElementById('curatorName');
  var roleEl = document.getElementById('curatorRole');
  var avatarEl = document.getElementById('curatorAvatar');
  if (nameEl) nameEl.textContent = curator.name;
  if (roleEl) roleEl.textContent = curator.role + ' · ' + curator.department;
  if (avatarEl) avatarEl.textContent = initials;
}

async function loadLiveDashboardData() {
  try {
    var stats = await ApiClient.getArtifactStats();
    var loanSummary = await ApiClient.getLoanSummary();

    document.getElementById('ovTotal').textContent = stats.total.toLocaleString('en-IN');
    document.getElementById('ovLoans').textContent = loanSummary.active + loanSummary.overdue;

    var barsWrap = document.getElementById('collectionBars');
    var maxCount = Math.max.apply(null, Object.values(stats.byCategory));
    barsWrap.innerHTML = Object.keys(stats.byCategory).map(function (cat) {
      var count = stats.byCategory[cat];
      var pct = Math.round((count / maxCount) * 100);
      return (
        '<div class="bar-row">' +
          '<div class="bar-label"><span>' + cat + '</span><span>' + count + '</span></div>' +
          '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%"></div></div>' +
        '</div>'
      );
    }).join('');

    var loansData = await ApiClient.getLoans({ tab: 'Active', page_size: 4 });
    document.getElementById('loanSummaryList').innerHTML = loansData.results.map(function (l) {
      var d = daysUntil(l.dueDate);
      var sub = l.status === 'Overdue' ? ('Overdue by ' + Math.abs(d) + ' days') : ('Due in ' + d + ' days');
      return (
        '<li>' +
          '<div><span class="item-name">' + l.artifact + '</span><span class="item-sub">' + l.borrower + '</span></div>' +
          '<span class="badge ' + (l.status === 'Overdue' ? 'badge-overdue' : 'badge-active') + '">' + sub + '</span>' +
        '</li>'
      );
    }).join('');

    showToast('Live data loaded from the ArtifactVault MongoDB backend.');
  } catch (err) {
    console.warn('Could not load live dashboard data, showing sample data instead.', err);
  }
}

/* ---------------------------------------------------------
   Shared helpers
   --------------------------------------------------------- */
function initNavToggle() {
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', function () {
    links.classList.toggle('open');
  });
}

function initFooterYear() {
  var els = document.querySelectorAll('.current-year');
  var year = new Date().getFullYear();
  els.forEach(function (el) { el.textContent = year; });
}

function showToast(message) {
  var existing = document.querySelector('.toast');
  if (existing) existing.remove();
  var toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(function () { toast.classList.add('show'); });
  setTimeout(function () {
    toast.classList.remove('show');
    setTimeout(function () { toast.remove(); }, 300);
  }, 3200);
}

function iconMarkup(key, extraClass) {
  return ICONS[key] || ICONS.artifacts;
}

function formatDate(iso) {
  var d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function daysUntil(iso) {
  var today = new Date('2026-06-28T00:00:00');
  var due = new Date(iso + 'T00:00:00');
  return Math.round((due - today) / 86400000);
}

function getParam(name) {
  var params = new URLSearchParams(window.location.search);
  return params.get(name);
}

/* ---------------------------------------------------------
   HOME PAGE
   --------------------------------------------------------- */
function initHomePage() {
  // Collections
  var collectionsGrid = document.getElementById('collectionsGrid');
  if (collectionsGrid) {
    collectionsGrid.innerHTML = COLLECTIONS.map(function (c) {
      var imgHtml = c.image
        ? '<div class="collection-img-wrap"><img src="' + c.image + '" alt="' + c.title + '" loading="lazy" onerror="this.parentElement.className=\'icon-wrap\';this.remove()"></div>'
        : '<div class="icon-wrap" style="color:var(--gold-dark)">' + iconMarkup(c.icon) + '</div>';
      return (
        '<div class="collection-card">' +
          imgHtml +
          '<h3>' + c.title + '</h3>' +
          '<span class="count">' + c.count + ' items catalogued</span>' +
          '<p>' + c.desc + '</p>' +
          '<a class="view-link" href="catalog.html?category=' + encodeURIComponent(c.key) + '">View Collection</a>' +
        '</div>'
      );
    }).join('');
  }

  // Featured artifacts — first 4
  var featured = ARTIFACTS.slice(0, 4);
  document.getElementById('featuredArtifacts').innerHTML = featured.map(renderArtifactCard).join('');

  // Stats counters
  var statTotal = document.getElementById('statTotal');
  var statLoans = document.getElementById('statLoans');
  var statCurators = document.getElementById('statCurators');
  if (statTotal) animateCount(statTotal, STATS.totalArtifacts);
  if (statLoans) animateCount(statLoans, STATS.activeLoans);
  if (statCurators) animateCount(statCurators, STATS.curators);

  // Testimonials
  var tWrap = document.getElementById('testimonialsGrid');
  if (tWrap) {
    tWrap.innerHTML = TESTIMONIALS.map(function (t) {
      var initials = t.name.split(' ').map(function (n) { return n[0]; }).join('').slice(0, 2);
      return (
        '<div class="testimonial-card">' +
          '<span class="quote-mark">&ldquo;</span>' +
          '<p class="quote">' + t.quote + '</p>' +
          '<div class="who">' +
            '<div class="avatar">' + initials + '</div>' +
            '<div class="meta"><strong>' + t.name + '</strong><span>' + t.role + '</span></div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }


  var heroSearch = document.getElementById('heroSearchForm');
  if (heroSearch) {
    heroSearch.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = document.getElementById('heroSearchInput').value.trim();
      window.location.href = 'catalog.html' + (q ? ('?q=' + encodeURIComponent(q)) : '');
    });
  }

  // Search chips
  document.querySelectorAll('.chip[data-cat]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      window.location.href = 'catalog.html?category=' + encodeURIComponent(chip.dataset.cat);
    });
  });
}

function renderArtifactCard(a) {
  var thumbHtml;
  if (a.image) {
    thumbHtml = (
      '<div class="artifact-thumb-real">' +
        '<img src="' + a.image + '" alt="' + a.name + '" loading="lazy"' +
        ' onerror="this.style.display=\'none\'">' +
        '<div class="thumb-fallback" style="color:var(--gold-dark)">' + iconMarkup(a.icon) + '</div>' +
      '</div>'
    );
  } else {
    thumbHtml = '<div class="artifact-thumb" style="color:var(--gold-dark)">' + iconMarkup(a.icon) + '</div>';
  }
  return (
    '<div class="artifact-card">' +
      '<span class="tag-punch"></span>' +
      '<span class="acc-no">' + a.id + '</span>' +
      thumbHtml +
      '<h3>' + a.name + '</h3>' +
      '<div class="artifact-meta-row">' +
        '<span>' + a.materialGroup + '</span>' +
        '<span>' + a.originGroup + '</span>' +
      '</div>' +
      '<div class="card-foot">' +
        '<span class="era-badge">' + a.eraGroup + '</span>' +
        '<a class="btn btn-outline btn-sm" href="artifact-details.html?id=' + a.id + '">View Details</a>' +
      '</div>' +
    '</div>'
  );
}

function animateCount(el, target) {
  var start = 0;
  var duration = 900;
  var startTime = null;
  function step(ts) {
    if (!startTime) startTime = ts;
    var progress = Math.min((ts - startTime) / duration, 1);
    el.textContent = Math.floor(progress * (target - start) + start).toLocaleString('en-IN');
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target.toLocaleString('en-IN');
  }
  requestAnimationFrame(step);
}


var catalogState = { page: 1, perPage: 6 };

function initCatalogPage() {
  populateFilterOptions();

  var initialCategory = getParam('category');
  var initialQuery = getParam('q');
  if (initialQuery) document.getElementById('catalogSearch').value = initialQuery;
  if (initialCategory) document.getElementById('filterCategory').value = initialCategory;

  ['catalogSearch', 'filterEra', 'filterMaterial', 'filterOrigin', 'filterCategory'].forEach(function (id) {
    var el = document.getElementById(id);
    if (!el) return;
    var evt = el.tagName === 'SELECT' ? 'change' : 'input';
    el.addEventListener(evt, function () { catalogState.page = 1; renderCatalog(); });
  });

  var resetBtn = document.getElementById('resetFilters');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      document.getElementById('catalogSearch').value = '';
      document.getElementById('filterEra').value = '';
      document.getElementById('filterMaterial').value = '';
      document.getElementById('filterOrigin').value = '';
      document.getElementById('filterCategory').value = '';
      catalogState.page = 1;
      renderCatalog();
    });
  }

  renderCatalog();
}

function populateFilterOptions() {
  var eras = uniqueSorted(ARTIFACTS.map(function (a) { return a.eraGroup; }));
  var materials = uniqueSorted(ARTIFACTS.map(function (a) { return a.materialGroup; }));
  var origins = uniqueSorted(ARTIFACTS.map(function (a) { return a.originGroup; }));
  var categories = uniqueSorted(ARTIFACTS.map(function (a) { return a.category; }));

  fillSelect('filterEra', eras, 'All Eras');
  fillSelect('filterMaterial', materials, 'All Materials');
  fillSelect('filterOrigin', origins, 'All Origins');
  fillSelect('filterCategory', categories, 'All Categories');
}

function uniqueSorted(arr) {
  return Array.from(new Set(arr)).sort();
}

function fillSelect(id, values, allLabel) {
  var sel = document.getElementById(id);
  if (!sel) return;
  sel.innerHTML = '<option value="">' + allLabel + '</option>' +
    values.map(function (v) { return '<option value="' + v + '">' + v + '</option>'; }).join('');
}

function getFilteredArtifacts() {
  var q = (document.getElementById('catalogSearch').value || '').toLowerCase().trim();
  var era = document.getElementById('filterEra').value;
  var material = document.getElementById('filterMaterial').value;
  var origin = document.getElementById('filterOrigin').value;
  var category = document.getElementById('filterCategory').value;

  return ARTIFACTS.filter(function (a) {
    if (era && a.eraGroup !== era) return false;
    if (material && a.materialGroup !== material) return false;
    if (origin && a.originGroup !== origin) return false;
    if (category && a.category !== category) return false;
    if (q) {
      var hay = (a.name + ' ' + a.era + ' ' + a.material + ' ' + a.origin + ' ' + a.category).toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    return true;
  });
}

function renderCatalog() {
  var results = getFilteredArtifacts();
  var grid = document.getElementById('catalogGrid');
  var countEl = document.getElementById('resultCount');
  var emptyState = document.getElementById('emptyState');

  countEl.innerHTML = '<strong>' + results.length + '</strong> artifact' + (results.length === 1 ? '' : 's') + ' found';

  if (results.length === 0) {
    grid.innerHTML = '';
    emptyState.classList.add('show');
    document.getElementById('paginationWrap').innerHTML = '';
    return;
  }
  emptyState.classList.remove('show');

  var totalPages = Math.max(1, Math.ceil(results.length / catalogState.perPage));
  if (catalogState.page > totalPages) catalogState.page = totalPages;
  var startIdx = (catalogState.page - 1) * catalogState.perPage;
  var pageItems = results.slice(startIdx, startIdx + catalogState.perPage);

  grid.innerHTML = pageItems.map(renderArtifactCard).join('');
  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  var wrap = document.getElementById('paginationWrap');
  if (totalPages <= 1) { wrap.innerHTML = ''; return; }
  var html = '<button data-page="prev" ' + (catalogState.page === 1 ? 'disabled' : '') + '>&laquo;</button>';
  for (var i = 1; i <= totalPages; i++) {
    html += '<button data-page="' + i + '" class="' + (i === catalogState.page ? 'active' : '') + '">' + i + '</button>';
  }
  html += '<button data-page="next" ' + (catalogState.page === totalPages ? 'disabled' : '') + '>&raquo;</button>';
  wrap.innerHTML = html;

  wrap.querySelectorAll('button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var p = btn.dataset.page;
      if (p === 'prev') catalogState.page = Math.max(1, catalogState.page - 1);
      else if (p === 'next') catalogState.page = Math.min(totalPages, catalogState.page + 1);
      else catalogState.page = parseInt(p, 10);
      renderCatalog();
      document.getElementById('catalogTop').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ---------------------------------------------------------
   ARTIFACT DETAILS PAGE
   --------------------------------------------------------- */
function initDetailsPage() {
  var id = getParam('id') || ARTIFACTS[0].id;
  var artifact = ARTIFACTS.find(function (a) { return a.id === id; }) || ARTIFACTS[0];
  renderArtifactDetail(artifact);
}

function statusClass(status) {
  if (status === 'Displayed') return 'status-displayed';
  if (status === 'On Loan') return 'status-loan';
  return 'status-storage';
}

function renderArtifactDetail(a) {
  document.title = a.name + ' — ArtifactVault';
  document.getElementById('breadcrumbName').textContent = a.name;
  document.getElementById('detailAccNo').textContent = a.id;
  document.getElementById('detailName').textContent = a.name;
  document.getElementById('detailCategory').textContent = a.category;

  var displayEl = document.getElementById('detailIcon');
  if (a.image) {
    displayEl.innerHTML =
      '<img src="' + a.image + '" alt="' + a.name + '"' +
      ' style="width:100%;height:100%;object-fit:cover;position:relative;z-index:1;"' +
      ' onerror="this.style.display=\'none\'">' +
      '<div class="detail-img-fallback" style="color:var(--gold-dark)">' + iconMarkup(a.icon) + '</div>';
    displayEl.style.padding = '0';
    displayEl.style.position = 'relative';
  } else {
    displayEl.innerHTML = iconMarkup(a.icon);
    displayEl.style.color = 'var(--gold-dark)';
  }
  document.getElementById('detailCaption').textContent = a.era + ' · ' + a.origin;

  document.getElementById('metaEra').textContent = a.era;
  document.getElementById('metaMaterial').textContent = a.material;
  document.getElementById('metaOrigin').textContent = a.origin;
  document.getElementById('metaDimensions').textContent = a.dimensions;
  document.getElementById('metaStatus').innerHTML = '<span class="status-pill ' + statusClass(a.status) + '">' + a.status + '</span>';
  document.getElementById('metaAdded').textContent = formatDate(a.dateAdded);
  document.getElementById('detailSignificance').textContent = a.significance;

  var related = ARTIFACTS.filter(function (r) { return r.category === a.category && r.id !== a.id; }).slice(0, 3);
  if (related.length === 0) related = ARTIFACTS.filter(function (r) { return r.id !== a.id; }).slice(0, 3);
  document.getElementById('relatedGrid').innerHTML = related.map(renderArtifactCard).join('');
}


function initDashboardPage() {
  var dateEl = document.getElementById('dashDate');
  if (dateEl) {
    dateEl.textContent = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  }

  // Overview numbers
  document.getElementById('ovTotal').textContent = STATS.totalArtifacts.toLocaleString('en-IN');
  document.getElementById('ovLoans').textContent = STATS.activeLoans;
  document.getElementById('ovCurators').textContent = STATS.curators;
  var pendingReturns = LOANS.filter(function (l) { return l.status === 'Active' && daysUntil(l.dueDate) <= 14; }).length;
  document.getElementById('ovPending').textContent = pendingReturns;

  // Recent artifacts table — sorted by dateAdded desc, top 6
  var recent = ARTIFACTS.slice().sort(function (a, b) { return new Date(b.dateAdded) - new Date(a.dateAdded); }).slice(0, 6);
  document.getElementById('recentTableBody').innerHTML = recent.map(function (a) {
    return (
      '<tr>' +
        '<td class="mono">' + a.id + '</td>' +
        '<td>' + a.name + '</td>' +
        '<td>' + a.category + '</td>' +
        '<td>' + a.eraGroup + '</td>' +
        '<td>' + formatDate(a.dateAdded) + '</td>' +
        '<td><span class="status-pill ' + statusClass(a.status) + '">' + a.status + '</span></td>' +
        '<td><div class="row-actions">' +
          '<a class="icon-btn" href="artifact-details.html?id=' + a.id + '" title="View">' + ICONS.eye + '</a>' +
          '<button class="icon-btn" type="button" title="Edit" onclick="showToast(\'Edit form is available in the full curator system.\')">' + ICONS.edit + '</button>' +
        '</div></td>' +
      '</tr>'
    );
  }).join('');

  // Collection statistics bars
  var byCategory = {};
  ARTIFACTS.forEach(function (a) { byCategory[a.category] = (byCategory[a.category] || 0) + 1; });
  var maxCount = Math.max.apply(null, Object.values(byCategory));
  var barsWrap = document.getElementById('collectionBars');
  barsWrap.innerHTML = Object.keys(byCategory).map(function (cat) {
    var count = byCategory[cat];
    var pct = Math.round((count / maxCount) * 100);
    return (
      '<div class="bar-row">' +
        '<div class="bar-label"><span>' + cat + '</span><span>' + count + '</span></div>' +
        '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%"></div></div>' +
      '</div>'
    );
  }).join('');

  // Loan tracking mini summary — soonest due active loans
  var upcoming = LOANS.filter(function (l) { return l.status === 'Active' || l.status === 'Overdue'; })
    .sort(function (a, b) { return daysUntil(a.dueDate) - daysUntil(b.dueDate); }).slice(0, 4);
  document.getElementById('loanSummaryList').innerHTML = upcoming.map(function (l) {
    var d = daysUntil(l.dueDate);
    var sub = l.status === 'Overdue' ? ('Overdue by ' + Math.abs(d) + ' days') : ('Due in ' + d + ' days');
    return (
      '<li>' +
        '<div><span class="item-name">' + l.artifact + '</span><span class="item-sub">' + l.borrower + '</span></div>' +
        '<span class="badge ' + (l.status === 'Overdue' ? 'badge-overdue' : 'badge-active') + '">' + sub + '</span>' +
      '</li>'
    );
  }).join('');

  // Quick actions
  document.querySelectorAll('.quick-action-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      showToast(btn.dataset.toast || 'This action is available in the full ArtifactVault system.');
    });
  });
}


var loanState = { tab: 'Active', query: '' };

function initLoansPage() {
  document.querySelectorAll('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      loanState.tab = btn.dataset.tab;
      renderLoans();
    });
  });

  var searchInput = document.getElementById('loanSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      loanState.query = searchInput.value.toLowerCase().trim();
      renderLoans();
    });
  }

  renderLoans();
}

function loanBadge(status, dueDate) {
  if (status === 'Returned') return '<span class="badge badge-returned">Returned</span>';
  if (status === 'Overdue') return '<span class="badge badge-overdue">Overdue</span>';
  var d = daysUntil(dueDate);
  if (d <= 7) return '<span class="badge badge-soon">Active · Due Soon</span>';
  return '<span class="badge badge-active">Active</span>';
}

function dueIndicator(loan) {
  if (loan.status === 'Returned') return '<span class="mono">' + formatDate(loan.dueDate) + '</span>';
  var d = daysUntil(loan.dueDate);
  if (loan.status === 'Overdue' || d < 0) {
    return '<span class="mono" style="color:var(--danger)">' + formatDate(loan.dueDate) + ' (overdue ' + Math.abs(d) + 'd)</span>';
  }
  if (d <= 7) return '<span class="mono" style="color:var(--warn)">' + formatDate(loan.dueDate) + ' (' + d + 'd left)</span>';
  return '<span class="mono">' + formatDate(loan.dueDate) + ' (' + d + 'd left)</span>';
}

function renderLoans() {
  var rows = LOANS.filter(function (l) {
    if (loanState.tab === 'Active' && !(l.status === 'Active' || l.status === 'Overdue')) return false;
    if (loanState.tab === 'Returned' && l.status !== 'Returned') return false;
    if (loanState.query) {
      var hay = (l.artifact + ' ' + l.borrower + ' ' + l.id + ' ' + l.contact).toLowerCase();
      if (hay.indexOf(loanState.query) === -1) return false;
    }
    return true;
  });

  var tbody = document.getElementById('loansTableBody');
  var emptyState = document.getElementById('loansEmptyState');

  if (rows.length === 0) {
    tbody.innerHTML = '';
    emptyState.classList.add('show');
  } else {
    emptyState.classList.remove('show');
    tbody.innerHTML = rows.map(function (l) {
      return (
        '<tr>' +
          '<td class="mono">' + l.id + '</td>' +
          '<td>' + l.artifact + '</td>' +
          '<td>' + l.borrower + '</td>' +
          '<td class="mono">' + formatDate(l.loanDate) + '</td>' +
          '<td>' + dueIndicator(l) + '</td>' +
          '<td>' + loanBadge(l.status, l.dueDate) + '</td>' +
          '<td><div class="row-actions">' +
            '<a class="icon-btn" href="artifact-details.html?id=' + l.artifactId + '" title="View artifact">' + ICONS.eye + '</a>' +
          '</div></td>' +
        '</tr>'
      );
    }).join('');
  }

  document.getElementById('loanResultCount').innerHTML = '<strong>' + rows.length + '</strong> record' + (rows.length === 1 ? '' : 's');
}