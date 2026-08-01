(function () {
  const input = document.getElementById('globalSearch');
  const resultsBox = document.getElementById('searchResults');
  let debounceTimer;

  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const query = this.value.trim();

    if (query.length < 2) {
      resultsBox.style.display = 'none';
      resultsBox.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => runSearch(query), 300);
  });

  function runSearch(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => renderResults(data))
      .catch(err => console.error('Search failed:', err));
  }

  function renderResults(data) {
    const hasResults = data.cases.length || data.suspects.length;

    if (!hasResults) {
      resultsBox.innerHTML = '<div class="search-empty">No matches found.</div>';
      resultsBox.style.display = 'block';
      return;
    }

    let html = '';

    if (data.cases.length) {
      html += '<div class="search-group-label">Cases</div>';
      data.cases.forEach(c => {
        html += `
          <a href="${c.url}" class="search-result-item">
            <span class="search-result-title">${escapeHtml(c.title)}</span>
            <span class="search-result-sub">#${escapeHtml(c.case_number)} • ${escapeHtml(c.status || '')}</span>
          </a>`;
      });
    }

    if (data.suspects.length) {
      html += '<div class="search-group-label">Suspects</div>';
      data.suspects.forEach(s => {
        html += `
          <a href="${s.url}" class="search-result-item">
            <span class="search-result-title">${escapeHtml(s.name)}</span>
            <span class="search-result-sub">${escapeHtml(s.occupation || '')} — ${escapeHtml(s.case_title)}</span>
          </a>`;
      });
    }

    resultsBox.innerHTML = html;
    resultsBox.style.display = 'block';
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-search')) {
      resultsBox.style.display = 'none';
    }
  });
})();