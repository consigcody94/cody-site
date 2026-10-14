// Progressive enhancement: everything is pre-rendered; this only adds issuer dropdown + search.
(function () {
  var tools = document.getElementById('tools');
  var q = document.getElementById('q');
  var empty = document.getElementById('empty');
  var sel = document.getElementById('issuer');
  var issuers = Array.prototype.slice.call(document.querySelectorAll('section.issuer'));
  var active = '';
  if (!tools) return;
  tools.hidden = false;
  function apply() {
    var term = q.value.trim().toLowerCase(), shown = 0;
    issuers.forEach(function (sec) {
      var okIssuer = !active || sec.getAttribute('data-issuer') === active, secShown = 0;
      sec.querySelectorAll('.cat').forEach(function (cat) {
        var catShown = 0;
        cat.querySelectorAll('.item').forEach(function (li) {
          var ok = okIssuer && (!term || li.getAttribute('data-search').indexOf(term) !== -1);
          li.hidden = !ok; if (ok) catShown++;
        });
        cat.hidden = catShown === 0; secShown += catShown;
      });
      sec.hidden = secShown === 0; shown += secShown;
    });
    empty.hidden = shown !== 0;
  }
  sel.addEventListener('change', function () { active = sel.value; apply(); });
  q.addEventListener('input', apply);
  var yr = document.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();
})();
