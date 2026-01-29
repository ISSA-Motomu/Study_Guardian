export const chartsModule = {
  data() {
    return {
      // Chart Data
      chartMode: 'thisWeek', // lastWeek, thisWeek, subjects
      weeklyActivityTitle: '今週の活動',
      weeklyData: [], // { label: 'Su 26', percent: 20 }
      lastWeekData: [],
      subjectData: [], // { label: 'Subject', percent: 30, color: '...' }
      touchStartX: 0,
    }
  },
  methods: {
    generateWeeklyData() {
      const now = new Date();
      // Calculate "This Week" (Sunday start)
      const todayDay = now.getDay(); // 0=Sun
      const sunday = new Date(now);
      sunday.setDate(now.getDate() - todayDay);
      const saturday = new Date(sunday);
      saturday.setDate(sunday.getDate() + 6);

      // Title func
      const fmt = d => `${d.getMonth() + 1}/${d.getDate()}`;
      const setTitle = (start, end) => `今週の活動 (${fmt(start)} - ${fmt(end)})`;

      this.weeklyActivityTitle = setTitle(sunday, saturday);

      // Generate Data
      const createWeekData = (startDate) => {
        return Array.from({ length: 7 }, (_, i) => {
          const d = new Date(startDate);
          d.setDate(startDate.getDate() + i);
          const isToday = d.toDateString() === now.toDateString();
          // Mock percentage
          const p = [20, 45, 30, 80, 10, 90, 60][i] || 30; // Use old values or random
          const isFuture = d > now;
          return {
            label: `${d.getMonth() + 1}/${d.getDate()}`,
            percent: isFuture ? 0 : p,
            isToday: isToday
          };
        });
      };

      this.weeklyData = createWeekData(sunday);

      const lastSunday = new Date(sunday);
      lastSunday.setDate(sunday.getDate() - 7);
      this.lastWeekData = createWeekData(lastSunday);

      // Mock Subject Data
      this.subjectData = [
        { label: '国語', percent: 30, color: '#F87171' },
        { label: '数学', percent: 40, color: '#60A5FA' },
        { label: '理科', percent: 20, color: '#34D399' },
        { label: '社会', percent: 10, color: '#FBBF24' },
      ];
    },
    onTouchStart(e) {
      this.touchStartX = e.changedTouches[0].screenX;
    },
    onTouchEnd(e) {
      this.touchEndX = e.changedTouches[0].screenX;
      this.handleSwipe();
    },
    handleSwipe() {
      const diff = this.touchEndX - this.touchStartX;
      const threshold = 50;
      if (Math.abs(diff) < threshold) return;

      // Order: Last Week <-> This Week <-> Subjects
      const order = ['lastWeek', 'thisWeek', 'subjects'];
      let idx = order.indexOf(this.chartMode);

      if (diff > 0) { // Swipe Right (Previous)
        if (idx > 0) idx--;
      } else { // Swipe Left (Next)
        if (idx < order.length - 1) idx++;
      }
      this.chartMode = order[idx];

      // Update Title
      if (this.chartMode === 'lastWeek') {
        const now = new Date();
        const d = new Date(now);
        d.setDate(d.getDate() - d.getDay() - 7);
        const sat = new Date(d);
        sat.setDate(d.getDate() + 6);
        const fmt = date => `${date.getMonth() + 1}/${date.getDate()}`;
        this.weeklyActivityTitle = `先週の活動 (${fmt(d)} - ${fmt(sat)})`;
      } else if (this.chartMode === 'thisWeek') {
        const now = new Date();
        const d = new Date(now);
        d.setDate(d.getDate() - d.getDay());
        const sat = new Date(d);
        sat.setDate(d.getDate() + 6);
        const fmt = date => `${date.getMonth() + 1}/${date.getDate()}`;
        this.weeklyActivityTitle = `今週の活動 (${fmt(d)} - ${fmt(sat)})`;
      } else {
        this.weeklyActivityTitle = '科目別比率';
      }
    },
  }
};