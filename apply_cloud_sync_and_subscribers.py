import re

print("Starting cloud sync and subscribers dashboard update...")

RTDB_URL_CONST = "https://gail-connect-d9e21-default-rtdb.firebaseio.com"

# ========================================================
# 1. UPDATE sweety.html & index.html
# ========================================================
with open('sweety.html', 'r', encoding='utf-8') as f:
    sw_content = f.read()

# Add RTDB_URL and syncToCloud helper
cloud_helper = f'''      const RTDB_URL = '{RTDB_URL_CONST}';

      function syncToCloud(item) {{
        if (!item || !item.id) return;
        try {{
          fetch(`${{RTDB_URL}}/submissions/${{item.id}}.json`, {{
            method: 'PUT',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(item)
          }}).catch(function () {{ }});

          if (item.isSubscribed && item.email) {{
            const subId = (item.id || '').replace('ENT-', 'SUB-');
            fetch(`${{RTDB_URL}}/subscribers/${{subId}}.json`, {{
              method: 'PUT',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{
                id: subId,
                name: item.name || 'Participant',
                email: item.email || '',
                city: item.city || 'India',
                score: item.score || 0,
                phase: item.phase || '',
                cycleId: item.cycleId || '',
                timestamp: item.timestamp || Date.now(),
                dateStr: item.dateStr || new Date().toLocaleString('en-IN')
              }})
            }}).catch(function () {{ }});
          }}
        }} catch (e) {{ }}
      }}
'''

# Insert cloud_helper before handleSubscribeClick
if "const RTDB_URL =" not in sw_content:
    sw_content = sw_content.replace(
        "window.handleSubscribeClick = function (e) {",
        cloud_helper + "\n      window.handleSubscribeClick = function (e) {"
    )
    print("Added RTDB_URL and syncToCloud helper to sweety.html")

# In handleSubscribeClick & handleResultSubscribeClick, sync subscriber to cloud
old_sub_handler = """        toast('🎉 Subscribed to @GAILIndiaLimited! Enjoy the challenge.');"""
new_sub_handler = """        toast('🎉 Subscribed to @GAILIndiaLimited! Enjoy the challenge.');

        // Instantly sync subscriber record to Cloud Realtime Database
        if (participantData && participantData.email) {
          const subId = 'SUB-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random() * 900 + 100);
          try {
            fetch(`${RTDB_URL}/subscribers/${subId}.json`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                id: subId,
                name: participantData.name || 'Participant',
                email: participantData.email,
                city: participantData.city || 'India',
                score: score || 0,
                timestamp: Date.now(),
                dateStr: new Date().toLocaleString('en-IN')
              })
            }).catch(function () {});
          } catch(e) {}
        }"""

if old_sub_handler in sw_content and "Instantly sync subscriber record to Cloud" not in sw_content:
    sw_content = sw_content.replace(old_sub_handler, new_sub_handler)
    print("Updated handleSubscribeClick cloud sync.")

# In handleGateSubmit: ensure isSubscribed is recorded and synced to cloud
gate_submit_target = """          if (existingIdx >= 0) {
            orgList[existingIdx] = { ...orgList[existingIdx], ...orgItem };
          } else {
            orgList.unshift(orgItem);
          }
          localStorage.setItem(STORAGE_KEY_ORGANIZER_LOG, JSON.stringify(orgList));
        } catch (err) { }"""

gate_submit_replacement = """          orgItem.isSubscribed = Boolean(isSubscribed);
          if (existingIdx >= 0) {
            orgList[existingIdx] = { ...orgList[existingIdx], ...orgItem };
          } else {
            orgList.unshift(orgItem);
          }
          localStorage.setItem(STORAGE_KEY_ORGANIZER_LOG, JSON.stringify(orgList));
          syncToCloud(orgItem);
        } catch (err) { }"""

if gate_submit_target in sw_content and "syncToCloud(orgItem);" not in sw_content:
    sw_content = sw_content.replace(gate_submit_target, gate_submit_replacement)
    print("Updated handleGateSubmit with cloud sync.")

# In Scene 12 result screen: sync updated entry to cloud
result_submit_target = """            if (existingIdx >= 0) {
              orgList[existingIdx] = { ...orgList[existingIdx], ...orgItem };
            } else {
              orgList.unshift(orgItem);
            }
            localStorage.setItem(STORAGE_KEY_ORGANIZER_LOG, JSON.stringify(orgList));
          } catch (e) { }"""

result_submit_replacement = """            orgItem.isSubscribed = Boolean(isSubscribed);
            if (existingIdx >= 0) {
              orgList[existingIdx] = { ...orgList[existingIdx], ...orgItem };
            } else {
              orgList.unshift(orgItem);
            }
            localStorage.setItem(STORAGE_KEY_ORGANIZER_LOG, JSON.stringify(orgList));
            syncToCloud(orgItem);
          } catch (e) { }"""

if result_submit_target in sw_content:
    sw_content = sw_content.replace(result_submit_target, result_submit_replacement)
    print("Updated Scene 12 with cloud sync.")

with open('sweety.html', 'w', encoding='utf-8') as f:
    f.write(sw_content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(sw_content)

print("sweety.html and index.html saved with cloud sync!")

# ========================================================
# 2. UPDATE organizer.html & admin.html
# ========================================================
with open('organizer.html', 'r', encoding='utf-8') as f:
    org = f.read()

# 2a. Add 5th KPI card: YouTube Subscribers
old_kpi_end = """        <div class="kpi-sub">
          <span id="kpiPeakScore">Peak: 0 pts</span>
        </div>
      </div>
    </section>"""

new_kpi_card = """        <div class="kpi-sub">
          <span id="kpiPeakScore">Peak: 0 pts</span>
        </div>
      </div>

      <div class="kpi-card kpi-purple" style="border-color:rgba(239, 68, 68, 0.4);background:radial-gradient(circle at 10% 10%, rgba(220, 38, 38, 0.15) 0%, #03140a 100%);">
        <div class="kpi-title">
          <span>YOUTUBE SUBSCRIBERS</span>
          <span class="kpi-icon">🔴</span>
        </div>
        <div class="kpi-value" id="kpiSubscribersCount">0</div>
        <div class="kpi-sub">
          <span id="kpiSubRate">0% of Participants Subscribed</span>
        </div>
      </div>
    </section>"""

if old_kpi_end in org and "kpiSubscribersCount" not in org:
    org = org.replace(old_kpi_end, new_kpi_card)
    print("Added Subscribers KPI card.")

# 2b. Add 6th Tab in navigation tabs
old_tabs_end = """      <button class="org-tab-btn" id="tabBtnCities" onclick="switchView('cities')">
        <span>🏙️ City-wise Analytics</span>
        <span class="tab-badge" id="badgeCitiesCount">0</span>
      </button>
    </div>"""

new_tabs_end = """      <button class="org-tab-btn" id="tabBtnCities" onclick="switchView('cities')">
        <span>🏙️ City-wise Analytics</span>
        <span class="tab-badge" id="badgeCitiesCount">0</span>
      </button>

      <button class="org-tab-btn" id="tabBtnSubscribers" onclick="switchView('subscribers')">
        <span>🔴 Subscribed Users</span>
        <span class="tab-badge" id="badgeSubscribersCount">0</span>
      </button>
    </div>"""

if old_tabs_end in org and "tabBtnSubscribers" not in org:
    org = org.replace(old_tabs_end, new_tabs_end)
    print("Added Subscribed Users tab button.")

# 2c. Add filter status option for Subscribed
old_filter_status = """          <select id="filterStatus" class="filter-select" onchange="filterAllEntries()">
            <option value="ALL">All Statuses</option>
            <option value="WINNER">🌱 Tree Winners Only</option>
            <option value="COOLDOWN">🔒 60-Day Cooldown</option>
            <option value="PARTICIPANT">⚡ Participants</option>
          </select>"""

new_filter_status = """          <select id="filterStatus" class="filter-select" onchange="filterAllEntries()">
            <option value="ALL">All Statuses</option>
            <option value="WINNER">🌱 Tree Winners Only</option>
            <option value="SUBSCRIBED">🔴 Subscribed Users Only</option>
            <option value="COOLDOWN">🔒 60-Day Cooldown</option>
            <option value="PARTICIPANT">⚡ Participants</option>
          </select>"""

if old_filter_status in org:
    org = org.replace(old_filter_status, new_filter_status)
    print("Added SUBSCRIBED option to filterStatus.")

# 2d. Add View 6 (Subscribers Section) before </main>
subscribers_section = """
    <!-- ==================== VIEW 6: SUBSCRIBED USERS DASHBOARD ==================== -->
    <section id="viewSubscribers" style="display:none;">
      <!-- Hero Subscriber Banner -->
      <div style="background:rgba(239, 68, 68, 0.08);border:1.5px solid rgba(239, 68, 68, 0.28);border-radius:14px;padding:20px 24px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
        <div>
          <div style="font-size:12px;font-weight:700;color:#fca5a5;text-transform:uppercase;letter-spacing:0.5px;">GAIL Social Engagement Hub</div>
          <h2 style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 6px;">Verified YouTube Subscribers (@GAILIndiaLimited)</h2>
          <p style="font-size:12.5px;color:var(--text-dim);max-width:680px;line-height:1.4;">
            Participants who engaged with <em>Sweety Ki Rasoi</em> and subscribed to GAIL India Limited on YouTube. Captures real-time submissions from all devices and outside links.
          </p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn-export" style="background:linear-gradient(135deg, #ef4444, #b91c1c);border-color:#fca5a5;" onclick="exportSubscribersToCSV()">
            <span>📥</span> <span>Export Subscribers CSV</span>
          </button>
          <button class="btn-secondary" onclick="copySubscribedEmails()">
            <span>📋</span> <span>Copy Subscriber Emails</span>
          </button>
        </div>
      </div>

      <!-- Subscribers Metric Cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:16px;margin-bottom:24px;">
        <div style="background:var(--emerald-card);border:1px solid rgba(239, 68, 68, 0.3);border-radius:12px;padding:16px;">
          <div style="font-size:11px;color:#fca5a5;font-weight:700;text-transform:uppercase;">TOTAL SUBSCRIBED NAMES & EMAILS</div>
          <div style="font-size:28px;font-weight:900;color:#fff;margin:4px 0;" id="subMetricTotal">0</div>
          <div style="font-size:11px;color:var(--text-dim);">Verified participant contact leads</div>
        </div>
        <div style="background:var(--emerald-card);border:1px solid rgba(74, 222, 128, 0.3);border-radius:12px;padding:16px;">
          <div style="font-size:11px;color:var(--accent-lime);font-weight:700;text-transform:uppercase;">SUBSCRIBED CITIES / TOWNS</div>
          <div style="font-size:28px;font-weight:900;color:#fff;margin:4px 0;" id="subMetricCities">0</div>
          <div style="font-size:11px;color:var(--text-dim);">Locations across India</div>
        </div>
        <div style="background:var(--emerald-card);border:1px solid rgba(244, 208, 63, 0.3);border-radius:12px;padding:16px;">
          <div style="font-size:11px;color:var(--gail-yellow);font-weight:700;text-transform:uppercase;">SUBSCRIPTION CONVERSION RATE</div>
          <div style="font-size:28px;font-weight:900;color:#fff;margin:4px 0;" id="subMetricRate">0%</div>
          <div style="font-size:11px;color:var(--text-dim);">Of total challenge participants</div>
        </div>
      </div>

      <!-- City-wise Subscription Distribution Chips -->
      <div style="background:var(--emerald-card);border:1px solid var(--emerald-border);border-radius:14px;padding:18px 20px;margin-bottom:24px;">
        <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
          <span>🏙️</span> <span>City-wise Subscriber Distribution</span>
        </div>
        <div id="subscribersCityChips" style="display:flex;flex-wrap:wrap;gap:8px;">
          <div style="font-size:12px;color:var(--text-dim);">Loading city subscribers...</div>
        </div>
      </div>

      <!-- Subscribers Table Toolbar -->
      <div class="toolbar-box">
        <div class="toolbar-left">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchSubscribersInput" class="search-input" placeholder="Search subscriber name, email, city..." oninput="filterSubscribersTable()" />
          </div>
          <select id="filterSubCity" class="filter-select" onchange="filterSubscribersTable()">
            <option value="ALL">All Subscribed Cities</option>
          </select>
        </div>
        <div class="toolbar-right">
          <span style="font-size:12px;color:var(--text-dim);" id="subscribersCountIndicator">Showing 0 subscribers</span>
        </div>
      </div>

      <!-- Subscribers Table -->
      <div class="table-card">
        <div class="table-responsive">
          <table class="org-table">
            <thead>
              <tr>
                <th style="width:40px;">#</th>
                <th>Subscriber Name</th>
                <th>Contact Email Address</th>
                <th>City / Location</th>
                <th>Contest Score</th>
                <th>Phase</th>
                <th>Subscription Status</th>
                <th>Subscribed Date</th>
              </tr>
            </thead>
            <tbody id="subscribersTableBody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </section>
"""

if "id=\"viewSubscribers\"" not in org:
    org = org.replace("  </main>", subscribers_section + "\n  </main>")
    print("Added viewSubscribers HTML section.")

# 2e. Update JS Engine: Cloud Realtime Database Sync + Subscribers Dashboard Logic
old_js_start = """      const STORAGE_KEY_ORGANIZER_LOG = 'gail_organizer_entries_v1';
      const STORAGE_KEY_PAST_WINNERS = 'gail_past_winners_v3';
      const SIXTY_DAYS_MS = 60 * 24 * 60 * 60 * 1000;

      let masterEntries = [];
      let currentTab = 'entries';"""

new_js_start = f"""      const RTDB_URL = '{RTDB_URL_CONST}';
      const STORAGE_KEY_ORGANIZER_LOG = 'gail_organizer_entries_v1';
      const STORAGE_KEY_PAST_WINNERS = 'gail_past_winners_v3';
      const SIXTY_DAYS_MS = 60 * 24 * 60 * 60 * 1000;

      let masterEntries = [];
      let subscribersList = [];
      let currentTab = 'entries';
      let isFetchingCloud = false;"""

if old_js_start in org:
    org = org.replace(old_js_start, new_js_start)
    print("Updated JS declarations with RTDB_URL and subscribersList.")

# Replace loadOrganizerData with full async cloud fetching & subscriber aggregation
old_load_fn_start = "      function loadOrganizerData() {"
# Find the start and end of loadOrganizerData function
load_idx = org.find(old_load_fn_start)
if load_idx != -1:
    save_idx = org.find("      function saveOrganizerData(data) {", load_idx)
    assert save_idx != -1, "saveOrganizerData not found"
    
    new_load_fn = """      async function loadOrganizerData() {
        if (isFetchingCloud) return;
        isFetchingCloud = true;

        let localList = [];
        try {
          const raw = localStorage.getItem(STORAGE_KEY_ORGANIZER_LOG);
          if (raw) localList = JSON.parse(raw);
        } catch (e) {}

        if (!Array.isArray(localList)) localList = [];
        localList = localList.filter(item => !isMockSampleEntry(item));

        // 1. Fetch real-time submissions from Cloud Realtime Database (captures ALL plays from outside links!)
        let cloudMap = {};
        try {
          const resp = await fetch(`${RTDB_URL}/submissions.json`);
          if (resp.ok) {
            cloudMap = await resp.json() || {};
          }
        } catch (e) {
          console.warn('Cloud submissions fetch error:', e);
        }

        // 2. Fetch subscribers from Cloud Realtime Database
        let cloudSubMap = {};
        try {
          const subResp = await fetch(`${RTDB_URL}/subscribers.json`);
          if (subResp.ok) {
            cloudSubMap = await subResp.json() || {};
          }
        } catch (e) {}

        // Merge local submissions and cloud submissions by entry ID
        const mergedMap = {};
        localList.forEach(item => {
          if (item && item.id) mergedMap[item.id] = item;
        });

        Object.values(cloudMap).forEach(item => {
          if (item && item.id && !isMockSampleEntry(item)) {
            mergedMap[item.id] = item;
          }
        });

        // Collect all subscribed emails from cloudSubMap
        const subEmailsSet = new Set(
          Object.values(cloudSubMap)
            .map(s => (s.email || '').trim().toLowerCase())
            .filter(Boolean)
        );

        let allEntries = Object.values(mergedMap).map(item => {
          const emailLower = (item.email || '').trim().toLowerCase();
          const isSub = Boolean(item.isSubscribed || subEmailsSet.has(emailLower));
          return { ...item, isSubscribed: isSub };
        });

        // 3. Also cross-import any real entries recorded in the leaderboard cycle
        try {
          const lbRaw = localStorage.getItem('gail_wah_kya_lb_cycle_v4');
          if (lbRaw) {
            const lbData = JSON.parse(lbRaw);
            if (lbData && Array.isArray(lbData.entries)) {
              const defaultNames = [
                'aarav sharma', 'kavita iyer', 'rohan gupta', 'priya patel', 
                'vikram malhotra', 'neha verma', 'deepak joshi', 'ananya roy', 
                'arjun kapoor', 'sunita rao'
              ];
              const cycleInfo = getContestCycleInfo();
              const now = new Date();
              const phaseName = cycleInfo.cycleId.endsWith('P1') ? 'Phase 1 (1st-10th)' : (cycleInfo.cycleId.endsWith('P2') ? 'Phase 2 (11th-20th)' : 'Phase 3 (21st-End)');

              lbData.entries.forEach(lbEntry => {
                const nameLower = (lbEntry.name || '').trim().toLowerCase();
                const hasEmail = Boolean(lbEntry.email && lbEntry.email.includes('@'));
                const isRealPlayer = hasEmail || (!defaultNames.includes(nameLower) && lbEntry.timestamp);
                if (isRealPlayer) {
                  const alreadyExists = allEntries.some(x => 
                    (x.email && lbEntry.email && x.email.toLowerCase() === lbEntry.email.toLowerCase()) ||
                    (x.name && x.name.toLowerCase() === nameLower && Math.abs((x.timestamp || 0) - (lbEntry.timestamp || 0)) < 60000)
                  );
                  if (!alreadyExists) {
                    allEntries.push({
                      id: 'ENT-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random() * 900 + 100),
                      name: lbEntry.name || 'Participant',
                      email: lbEntry.email || '',
                      city: lbEntry.city || 'India',
                      score: Number(lbEntry.score) || 0,
                      gameScore: Number(lbEntry.gameScore) || Number(lbEntry.score) || 0,
                      ytBonus: Number(lbEntry.ytBonus) || 0,
                      time: Number(lbEntry.time) || 32,
                      rating: calculateRating(lbEntry.score, lbEntry.time),
                      cycleId: lbData.cycleId || cycleInfo.cycleId,
                      phase: phaseName,
                      month: now.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }),
                      monthKey: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`,
                      isSubscribed: Boolean(lbEntry.isSubscribed || subEmailsSet.has((lbEntry.email || '').toLowerCase())),
                      timestamp: lbEntry.timestamp || Date.now(),
                      dateStr: lbEntry.timestamp ? new Date(lbEntry.timestamp).toLocaleString('en-IN') : now.toLocaleString('en-IN')
                    });
                  }
                }
              });
            }
          }
        } catch (e) {}

        // 4. Process dynamic winners, trees, ratings, and cooldowns
        masterEntries = processRealEntriesAndWinners(allEntries);

        // 5. Build unified subscribers list
        const subMap = {};
        masterEntries.forEach(item => {
          if (item.isSubscribed) {
            const key = (item.email || item.name || '').trim().toLowerCase();
            if (key) {
              subMap[key] = {
                name: item.name || 'Participant',
                email: item.email || '',
                city: item.city || 'India',
                score: item.score || 0,
                phase: item.phase || item.cycleId || 'Active Phase',
                dateStr: item.dateStr || 'Recent',
                timestamp: item.timestamp || Date.now()
              };
            }
          }
        });

        Object.values(cloudSubMap).forEach(s => {
          const key = (s.email || s.name || '').trim().toLowerCase();
          if (key && !subMap[key]) {
            subMap[key] = {
              name: s.name || 'Participant',
              email: s.email || '',
              city: s.city || 'India',
              score: s.score || 0,
              phase: s.phase || s.cycleId || 'Active Phase',
              dateStr: s.dateStr || 'Recent',
              timestamp: s.timestamp || Date.now()
            };
          }
        });

        subscribersList = Object.values(subMap).sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));

        // Save sanitized list to local storage
        saveOrganizerData(masterEntries);
        isFetchingCloud = false;

        // Render all views
        renderDashboard();
      }
"""
    org = org[:load_idx] + new_load_fn + "\n" + org[save_idx:]
    print("Replaced loadOrganizerData with async cloud fetcher.")

# Update switchView to handle 'subscribers'
old_switch_views = """        const views = {
          entries: document.getElementById('viewEntries'),
          winners: document.getElementById('viewWinners'),
          phases: document.getElementById('viewPhases'),
          months: document.getElementById('viewMonths'),
          cities: document.getElementById('viewCities')
        };

        const buttons = {
          entries: document.getElementById('tabBtnEntries'),
          winners: document.getElementById('tabBtnWinners'),
          phases: document.getElementById('tabBtnPhases'),
          months: document.getElementById('tabBtnMonths'),
          cities: document.getElementById('tabBtnCities')
        };"""

new_switch_views = """        const views = {
          entries: document.getElementById('viewEntries'),
          winners: document.getElementById('viewWinners'),
          phases: document.getElementById('viewPhases'),
          months: document.getElementById('viewMonths'),
          cities: document.getElementById('viewCities'),
          subscribers: document.getElementById('viewSubscribers')
        };

        const buttons = {
          entries: document.getElementById('tabBtnEntries'),
          winners: document.getElementById('tabBtnWinners'),
          phases: document.getElementById('tabBtnPhases'),
          months: document.getElementById('tabBtnMonths'),
          cities: document.getElementById('tabBtnCities'),
          subscribers: document.getElementById('tabBtnSubscribers')
        };"""

if old_switch_views in org:
    org = org.replace(old_switch_views, new_switch_views)
    print("Updated switchView with subscribers view.")

# Update updateKpis to include subscribers count & conversion rate
old_kpis_fn = """        document.getElementById('kpiTotalParticipants').textContent = total.toLocaleString();
        document.getElementById('kpiTreeWinners').textContent = winners.toLocaleString();
        document.getElementById('kpiCitiesCount').textContent = cities;
        document.getElementById('kpiAvgScore').textContent = `${avgScore} pts`;
        document.getElementById('kpiPeakScore').textContent = `Peak: ${peakScore} pts`;

        document.getElementById('badgeAllCount').textContent = total;
        document.getElementById('badgeWinnersCount').textContent = winners;
        document.getElementById('badgeCitiesCount').textContent = cities;"""

new_kpis_fn = """        document.getElementById('kpiTotalParticipants').textContent = total.toLocaleString();
        document.getElementById('kpiTreeWinners').textContent = winners.toLocaleString();
        document.getElementById('kpiCitiesCount').textContent = cities;
        document.getElementById('kpiAvgScore').textContent = `${avgScore} pts`;
        document.getElementById('kpiPeakScore').textContent = `Peak: ${peakScore} pts`;

        const subCount = subscribersList.length;
        const subRate = total > 0 ? Math.round((subCount / total) * 100) : 0;
        const kpiSubEl = document.getElementById('kpiSubscribersCount');
        const kpiSubRateEl = document.getElementById('kpiSubRate');
        if (kpiSubEl) kpiSubEl.textContent = subCount.toLocaleString();
        if (kpiSubRateEl) kpiSubRateEl.textContent = `${subRate}% of Participants Subscribed`;

        document.getElementById('badgeAllCount').textContent = total;
        document.getElementById('badgeWinnersCount').textContent = winners;
        document.getElementById('badgeCitiesCount').textContent = cities;
        const badgeSubEl = document.getElementById('badgeSubscribersCount');
        if (badgeSubEl) badgeSubEl.textContent = subCount.toLocaleString();"""

if old_kpis_fn in org:
    org = org.replace(old_kpis_fn, new_kpis_fn)
    print("Updated updateKpis with subscribers metrics.")

# Update getFilteredEntries to support statusFilter === 'SUBSCRIBED'
old_status_filter = """          if (statusFilter === 'WINNER' && !item.isWinner) return false;
          if (statusFilter === 'COOLDOWN' && !item.isCooldown) return false;
          if (statusFilter === 'PARTICIPANT' && (item.isWinner || item.isCooldown)) return false;"""

new_status_filter = """          if (statusFilter === 'WINNER' && !item.isWinner) return false;
          if (statusFilter === 'SUBSCRIBED' && !item.isSubscribed) return false;
          if (statusFilter === 'COOLDOWN' && !item.isCooldown) return false;
          if (statusFilter === 'PARTICIPANT' && (item.isWinner || item.isCooldown)) return false;"""

if old_status_filter in org:
    org = org.replace(old_status_filter, new_status_filter)
    print("Updated getFilteredEntries with SUBSCRIBED filter.")

# Update renderDashboard to also call renderSubscribersView()
old_render_dash = """      function renderDashboard() {
        updateHeroCycleInfo();
        updateKpis();
        renderAllEntriesTable();
        renderWinnersTable();
        renderPhasesView();
        renderMonthsView();
        renderCitiesView();
      }"""

new_render_dash = """      function renderDashboard() {
        updateHeroCycleInfo();
        updateKpis();
        renderAllEntriesTable();
        renderWinnersTable();
        renderPhasesView();
        renderMonthsView();
        renderCitiesView();
        renderSubscribersView();
      }"""

if old_render_dash in org:
    org = org.replace(old_render_dash, new_render_dash)
    print("Updated renderDashboard to call renderSubscribersView.")

# Add Subscribers View Implementation functions (filter, table, copy, export)
subscribers_js_code = """
      // --- VIEW 6: SUBSCRIBED USERS DASHBOARD IMPLEMENTATION ---
      window.filterSubscribersTable = function() {
        renderSubscribersTable();
      };

      function getFilteredSubscribers() {
        const query = (document.getElementById('searchSubscribersInput')?.value || '').trim().toLowerCase();
        const cityFilter = document.getElementById('filterSubCity')?.value || 'ALL';

        return subscribersList.filter(item => {
          if (query) {
            const name = (item.name || '').toLowerCase();
            const email = (item.email || '').toLowerCase();
            const city = (item.city || '').toLowerCase();
            if (!name.includes(query) && !email.includes(query) && !city.includes(query)) return false;
          }
          if (cityFilter !== 'ALL') {
            if ((item.city || '').toLowerCase() !== cityFilter.toLowerCase()) return false;
          }
          return true;
        });
      }

      function renderSubscribersView() {
        const total = subscribersList.length;
        const totalParticipants = masterEntries.length;
        const cities = Array.from(new Set(subscribersList.map(s => (s.city || 'India').trim()))).filter(Boolean);
        const convRate = totalParticipants > 0 ? Math.round((total / totalParticipants) * 100) : 0;

        const elTotal = document.getElementById('subMetricTotal');
        const elCities = document.getElementById('subMetricCities');
        const elRate = document.getElementById('subMetricRate');
        if (elTotal) elTotal.textContent = total.toLocaleString();
        if (elCities) elCities.textContent = cities.length;
        if (elRate) elRate.textContent = `${convRate}%`;

        // Populate City Filter Dropdown
        const selectCity = document.getElementById('filterSubCity');
        if (selectCity) {
          const currentVal = selectCity.value;
          selectCity.innerHTML = '<option value="ALL">All Subscribed Cities (' + cities.length + ')</option>' +
            cities.sort().map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
          if (currentVal && Array.from(selectCity.options).some(o => o.value === currentVal)) {
            selectCity.value = currentVal;
          }
        }

        // Render City Distribution Chips
        const chipsContainer = document.getElementById('subscribersCityChips');
        if (chipsContainer) {
          const cityCounts = {};
          subscribersList.forEach(s => {
            const c = (s.city || 'India').trim();
            cityCounts[c] = (cityCounts[c] || 0) + 1;
          });
          const sortedCities = Object.entries(cityCounts).sort((a,b) => b[1] - a[1]);
          if (sortedCities.length === 0) {
            chipsContainer.innerHTML = '<div style="font-size:12px;color:var(--text-dim);">No subscribers recorded yet.</div>';
          } else {
            chipsContainer.innerHTML = sortedCities.map(([cityName, cnt]) => `
              <div style="background:rgba(239, 68, 68, 0.15);border:1px solid rgba(239, 68, 68, 0.4);color:#fecaca;padding:4px 10px;border-radius:20px;font-size:11.5px;font-weight:600;display:inline-flex;align-items:center;gap:5px;cursor:pointer;" onclick="filterSubByCityDirect('${escapeHtml(cityName)}')">
                <span>📍 ${escapeHtml(cityName)}</span>
                <span style="background:#ef4444;color:#fff;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:800;">${cnt}</span>
              </div>
            `).join('');
          }
        }

        renderSubscribersTable();
      }

      window.filterSubByCityDirect = function(cityName) {
        const select = document.getElementById('filterSubCity');
        if (select) {
          select.value = cityName;
          filterSubscribersTable();
        }
      };

      function renderSubscribersTable() {
        const tbody = document.getElementById('subscribersTableBody');
        const countInd = document.getElementById('subscribersCountIndicator');
        if (!tbody) return;

        const filtered = getFilteredSubscribers();
        if (countInd) countInd.textContent = `Showing ${filtered.length} of ${subscribersList.length} subscribers`;

        if (subscribersList.length === 0) {
          tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:40px 20px;color:var(--text-dim);">
            <div style="font-size:32px;margin-bottom:10px;">🔴</div>
            <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:6px;">No Verified Subscribers Recorded Yet</div>
            <div style="font-size:12px;color:var(--text-dim);max-width:500px;margin:0 auto;line-height:1.4;">
              Subscribers from all outside links and mobile devices playing <em>Sweety Ki Rasoi</em> will appear here automatically in real time via Cloud Sync.
            </div>
          </td></tr>`;
          return;
        }

        if (filtered.length === 0) {
          tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:30px;color:var(--text-dim);">No subscribers found matching filter criteria.</td></tr>`;
          return;
        }

        tbody.innerHTML = filtered.map((item, idx) => {
          const safeEmail = escapeHtml(item.email || 'subscriber@gail.co.in');
          return `<tr>
            <td style="font-weight:700;color:var(--text-dim);">${idx + 1}</td>
            <td>
              <div class="user-name-cell">
                <span style="font-weight:700;color:#fff;">${escapeHtml(item.name || 'Participant')}</span>
              </div>
            </td>
            <td>
              <div class="email-cell">
                <a href="mailto:${safeEmail}" style="color:inherit;text-decoration:none;">${safeEmail}</a>
                <button class="email-copy-btn" onclick="copyText('${safeEmail}')" title="Copy email">📋</button>
              </div>
            </td>
            <td>
              <span class="city-badge">📍 ${escapeHtml(item.city || 'India')}</span>
            </td>
            <td>
              <span class="score-chip">${item.score || 0} pts</span>
            </td>
            <td>
              <div style="font-size:11px;color:#a7f3d0;">${escapeHtml(item.phase || 'Active')}</div>
            </td>
            <td>
              <span class="badge-status" style="background:rgba(239, 68, 68, 0.2);border:1px solid #ef4444;color:#fecaca;">
                ✓ Subscribed @GAILIndiaLimited
              </span>
            </td>
            <td style="font-size:11px;color:var(--text-dim);white-space:nowrap;">
              ${escapeHtml(item.dateStr || 'Recent')}
            </td>
          </tr>`;
        }).join('');
      }

      window.copySubscribedEmails = function() {
        const validEmails = subscribersList
          .map(x => (x.email || '').trim())
          .filter(e => e && e.includes('@'));

        const unique = Array.from(new Set(validEmails));
        if (unique.length === 0) {
          alert('No subscribed email addresses available to copy.');
          return;
        }

        copyText(unique.join(', '));
        showToast(`📋 Copied ${unique.length} verified subscriber emails!`);
      };

      window.exportSubscribersToCSV = function() {
        const filtered = getFilteredSubscribers();
        if (filtered.length === 0) {
          alert('No subscribers to export.');
          return;
        }

        const headers = ['#', 'Subscriber Name', 'Email Address', 'City / Location', 'Contest Score', 'Contest Phase', 'Subscription Date', 'Channel'];
        const rows = filtered.map((s, idx) => [
          idx + 1,
          `"${(s.name || '').replace(/"/g, '""')}"`,
          `"${(s.email || '').replace(/"/g, '""')}"`,
          `"${(s.city || '').replace(/"/g, '""')}"`,
          s.score || 0,
          `"${s.phase || ''}"`,
          `"${s.dateStr || ''}"`,
          `"@GAILIndiaLimited"`
        ]);

        const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\\r\\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `GAIL_YouTube_Subscribers_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast('✅ Subscribers list exported to CSV!');
      };
"""

# Insert subscribers_js_code before "window.openAddEntryModal"
if "window.openAddEntryModal =" in org and "renderSubscribersView" not in org:
    org = org.replace("      window.openAddEntryModal =", subscribers_js_code + "\n      window.openAddEntryModal =")
    print("Added Subscribers View implementation methods.")

# Add subscription badge in All Entries table row
old_table_badge = """          let statusBadge = `<span class="badge-status status-participant">⚡ Participant</span>`;
          if (item.isWinner) {
            statusBadge = `<span class="badge-status status-winner">🌱 Tree Winner</span>`;
          } else if (item.isCooldown) {
            statusBadge = `<span class="badge-status status-cooldown">🔒 60d Cooldown (${item.cooldownDaysLeft || 45}d)</span>`;
          }"""

new_table_badge = """          let statusBadge = `<span class="badge-status status-participant">⚡ Participant</span>`;
          if (item.isWinner) {
            statusBadge = `<span class="badge-status status-winner">🌱 Tree Winner</span>`;
          } else if (item.isCooldown) {
            statusBadge = `<span class="badge-status status-cooldown">🔒 60d Cooldown (${item.cooldownDaysLeft || 45}d)</span>`;
          }
          if (item.isSubscribed) {
            statusBadge += `<span class="badge-status" style="background:rgba(239,68,68,0.2);border:1px solid #ef4444;color:#fca5a5;margin-left:4px;" title="Subscribed to GAIL YouTube">🔴 Subscribed</span>`;
          }"""

if old_table_badge in org:
    org = org.replace(old_table_badge, new_table_badge)
    print("Added subscription badge in All Entries table.")

# In handleManualAddEntry, also sync to cloud
old_manual_save = """        masterEntries.unshift(newRecord);
        saveOrganizerData(masterEntries);
        closeAddEntryModal();
        renderDashboard();
        showToast('✓ New participant entry successfully recorded!');"""

new_manual_save = """        masterEntries.unshift(newRecord);
        saveOrganizerData(masterEntries);
        // Sync to Cloud Realtime Database
        try {
          fetch(`${RTDB_URL}/submissions/${newRecord.id}.json`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newRecord)
          }).catch(function() {});
        } catch(e) {}
        closeAddEntryModal();
        renderDashboard();
        showToast('✓ New participant entry successfully recorded and synced to cloud!');"""

if old_manual_save in org:
    org = org.replace(old_manual_save, new_manual_save)
    print("Updated handleManualAddEntry to sync to cloud.")

with open('organizer.html', 'w', encoding='utf-8') as f:
    f.write(org)

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(org)

print("organizer.html and admin.html saved with cloud sync and subscribers dashboard!")
