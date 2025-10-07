const STORAGE_KEYS = {
    COLLAPSED_APPS: 'django_global_search_collapsed_apps',
    SELECTED_MODELS: 'django_global_search_selected_models'
};


const Storage = {
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('localStorage unavailable:', e);
        }
    }
};

const State = {
    getCollapsedApps() {
        return Storage.get(STORAGE_KEYS.COLLAPSED_APPS, {});
    },

    saveCollapsedApps(collapsedApps) {
        Storage.set(STORAGE_KEYS.COLLAPSED_APPS, collapsedApps);
    },

    getCurrentCollapsedApps() {
        const collapsed = {};
        document.querySelectorAll('.models-list').forEach(list => {
            const app = list.dataset.app;
            if (list.classList.contains('is-collapsed')) {
                collapsed[app] = true;
            }
        });
        return collapsed;
    },

    // Selection state
    getSelectedModels() {
        return Storage.get(STORAGE_KEYS.SELECTED_MODELS, []);
    },

    saveSelectedModels(selectedIds) {
        Storage.set(STORAGE_KEYS.SELECTED_MODELS, selectedIds);
    },

    getCurrentSelectedModels() {
        return Array.from(document.querySelectorAll('.model-checkbox:checked'))
            .map(cb => parseInt(cb.value, 10));
    }
};

class GlobalSearchUI {
    constructor() {
        this.appsInput = document.getElementById('apps-input');
        this.contentTypeInput = document.getElementById('content-type-input');
        this.searchAppsInput = document.getElementById('search-apps-input');
        this.searchContentTypeInput = document.getElementById('search-content-type-input');
        this.searchForm = document.getElementById('search-form');
        this.modelSelectionForm = document.getElementById('model-selection-form');

        if (!this.appsInput || !this.contentTypeInput || !this.searchForm || !this.modelSelectionForm) {
            return;
        }

        this.init();
    }

    init() {
        this.restoreState();
        this.updateAppCheckboxStates();
        this.updateFormParams();
        this.attachEventListeners();
    }

    restoreState() {
        this.restoreCollapseState();
        this.restoreSelectionState();
    }

    restoreCollapseState() {
        const collapsed = State.getCollapsedApps();
        
        document.querySelectorAll('.app-group').forEach(group => {
            const toggleBtn = group.querySelector('.toggle-btn');
            const app = toggleBtn.dataset.app;
            const modelsList = group.querySelector('.models-list');
            
            if (collapsed[app]) {
                modelsList.classList.add('is-collapsed');
                toggleBtn.textContent = '▶';
            }
        });
    }

    restoreSelectionState() {
        // Skip if URL has content_type parameter (server-side selection)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('content_type')) return;

        const saved = State.getSelectedModels();
        if (!saved.length) return;

        document.querySelectorAll('.model-checkbox').forEach(cb => {
            cb.checked = saved.includes(parseInt(cb.value, 10));
        });
    }

    attachEventListeners() {
        // Collapse/expand toggle
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleToggle(e));
        });

        // App checkbox (select/deselect all models in app)
        document.querySelectorAll('.app-checkbox').forEach(cb => {
            cb.addEventListener('change', (e) => this.handleAppCheckbox(e));
        });

        // Model checkbox
        document.querySelectorAll('.model-checkbox').forEach(cb => {
            cb.addEventListener('change', () => this.handleModelCheckbox());
        });

        // Bulk actions
        document.getElementById('select-all')
            .addEventListener('click', () => this.selectAll());
        document.getElementById('deselect-all')
            .addEventListener('click', () => this.deselectAll());

        // Save state when search form is submitted (only if search is successful)
        this.searchForm.addEventListener('submit', (e) => { 
            const searchContainer = document.querySelector('.search-container');
            const isSearchSuccessful = searchContainer && 
                searchContainer.getAttribute('data-search-success') === 'true';
            
            if (isSearchSuccessful) {
                this.saveState();
            }
        });
        
        // Save state when Apply button (model selection form) is submitted
        this.modelSelectionForm.addEventListener('submit', () => this.saveState());
    }

    handleToggle(e) {
        const btn = e.target;
        const modelsList = btn.closest('.app-group').querySelector('.models-list');
        
        modelsList.classList.toggle('is-collapsed');
        btn.textContent = modelsList.classList.contains('is-collapsed') ? '▶' : '▼';
    }

    handleAppCheckbox(e) {
        const app = e.target.dataset.app;
        const checked = e.target.checked;

        this.getModelCheckboxes(app).forEach(cb => cb.checked = checked);
        this.updateFormParams();
    }

    handleModelCheckbox() {
        this.updateAppCheckboxStates();
        this.updateFormParams();
    }

    selectAll() {
        document.querySelectorAll('.app-checkbox, .model-checkbox')
            .forEach(cb => cb.checked = true);
        this.updateAppCheckboxStates();
        this.updateFormParams();
    }

    deselectAll() {
        document.querySelectorAll('.app-checkbox, .model-checkbox')
            .forEach(cb => cb.checked = false);
        document.querySelectorAll('.app-checkbox')
            .forEach(cb => cb.indeterminate = false);
        this.updateFormParams();
    }

    updateAppCheckboxStates() {
        document.querySelectorAll('.app-checkbox').forEach(appCb => {
            const app = appCb.dataset.app;
            const modelCbs = this.getModelCheckboxes(app);
            const checkedCount = modelCbs.filter(cb => cb.checked).length;
            
            if (checkedCount === 0) {
                appCb.checked = false;
                appCb.indeterminate = false;
            } else if (checkedCount === modelCbs.length) {
                appCb.checked = true;
                appCb.indeterminate = false;
            } else {
                appCb.checked = false;
                appCb.indeterminate = true;
            }
        });
    }

    updateFormParams() {
        const checkedModelsByApp = this.getCheckedModelsByApp();

        const fullApps = [];
        const partialModels = [];

        for (const [app, modelIds] of Object.entries(checkedModelsByApp)) {
            const totalModels = this.getTotalModelsInApp(app);

            if (modelIds.length === totalModels) {
                // All models in this app are selected -> use 'apps' parameter
                fullApps.push(app);
            } else if (modelIds.length > 0) {
                // Only some models selected -> use 'content_type' parameter
                partialModels.push(...modelIds);
            }
        }

        // Update both sidebar form and search form
        this.appsInput.value = fullApps.join(',');
        this.contentTypeInput.value = partialModels.join(',');
        this.searchAppsInput.value = fullApps.join(',');
        this.searchContentTypeInput.value = partialModels.join(',');
    }

    // Save to localStorage when search button is clicked
    saveState() {
        State.saveCollapsedApps(State.getCurrentCollapsedApps());
        State.saveSelectedModels(State.getCurrentSelectedModels());
    }

    getModelCheckboxes(app) {
        return Array.from(document.querySelectorAll(`.model-checkbox[data-app="${app}"]`));
    }

    getCheckedModelIds() {
        return Array.from(document.querySelectorAll('.model-checkbox:checked'))
            .map(cb => cb.value);
    }

    getCheckedModelsByApp() {
        const modelsByApp = {};

        document.querySelectorAll('.model-checkbox:checked').forEach(cb => {
            const app = cb.dataset.app;
            const modelId = cb.value;

            if (!modelsByApp[app]) {
                modelsByApp[app] = [];
            }
            modelsByApp[app].push(modelId);
        });

        return modelsByApp;
    }

    getTotalModelsInApp(app) {
        return document.querySelectorAll(`.model-checkbox[data-app="${app}"]`).length;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new GlobalSearchUI();
});