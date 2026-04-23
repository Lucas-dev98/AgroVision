# Frontend Test Failure Analysis - AgroVision

**Status**: 99 failing tests / 397 total (298 passing)  
**Analysis Date**: April 21, 2026

## Executive Summary

The test failures follow **5 major systemic patterns** rather than scattered issues. All can be fixed with targeted updates to test expectations and component implementations.

---

## TOP 5 MOST COMMON FAILURE PATTERNS

### 1. **CSS CLASS NAMING MISMATCH (CRITICAL) - ~35-40 failures**
**Severity**: HIGH | **Impact**: Input, Card, SearchBar, AnimalDetail tests

**Root Cause**: Tests expect Tailwind CSS utility classes, but components use **BEM (Block-Element-Modifier) CSS methodology**.

**Evidence**:
- **Input.test.tsx** line 35: `expect(errorMsg).toHaveClass('text-red-600')`  
  Component uses: `.input-error` (CSS module class)
- **Input.test.tsx** line 42: `expect(helperText).toHaveClass('text-gray-500')`  
  Component uses: `.input-helper` (CSS module class)
- **Input.test.tsx** line 54: `expect(wrapper).toHaveClass('w-full')`  
  Component uses: `.input-wrapper` (CSS module class)
- **Card.test.tsx** line 23: `expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow-md', 'p-4')`  
  Component uses: `.card`, `.card--clickable`, `.card__title`, `.card__content` (BEM classes)

**Fix Strategy**: Update tests to check for actual BEM class names from components' CSS files

---

### 2. **querySelector SELECTOR EXPECTATIONS - ~20-25 failures**
**Severity**: HIGH | **Impact**: AnimalDetail, SearchBar, complex organism tests

**Root Cause**: Tests use `container.querySelector()` looking for classes that don't exist on the expected elements.

**Evidence**:
- **AnimalDetail.test.tsx** line 23: `container.querySelector('.animal-detail__breadcrumb')`  
  Component structure likely nests this differently
- **SearchBar.test.tsx** line 144: `container.querySelector('.search-bar')`  
  Component may structure wrapper differently
- **AnimalDetail.test.tsx** line 29: `container.querySelector('.animal-detail__card')`  
  Card is a separate component, not a query selector target

**Pattern**: Tests assume querySelector will find elements by CSS classes, but actual DOM structure varies

**Fix Strategy**: 
- Use React Testing Library queries instead of querySelector where possible
- Use `screen.getByRole()`, `screen.getByText()` for semantic queries
- Only use querySelector for CSS class verification on specific elements

---

### 3. **MOCK PROVIDER/CONTEXT MISMATCH - ~15-20 failures**
**Severity**: MEDIUM | **Impact**: LoginForm, RegisterForm, organisms with dependencies

**Root Cause**: Component hierarchy requires providers (Router, Auth Context, etc.) but tests may not have complete mock setup.

**Evidence**:
- **LoginForm.test.tsx** line 20: Mocks authService but component uses `useNavigate()`, needs BrowserRouter wrapper
- Tests wrap in `<BrowserRouter>` but may need additional context providers
- Some components reference hooks like `useMFA`, `useAuth` that aren't mocked
- Mock authService return types might not match actual API responses

**Pattern**: Tests mock one service but component has cascading dependencies

**Fix Strategy**:
- Create a centralized test wrapper with all required providers
- Mock all hooks that components depend on (`useMFA`, `useAuth`, etc.)
- Verify mock return structures match actual component expectations

---

### 4. **FORM VALIDATION ASSERTION TIMING - ~15-18 failures**
**Severity**: MEDIUM | **Impact**: LoginForm (11 failed), RegisterForm (8 failed), validation tests

**Root Cause**: Tests check for error messages but don't account for component's state update flow.

**Evidence**:
- **LoginForm.test.tsx** line 53: `await waitFor(() => { expect(screen.getByText(/CPF\/CNPJ é obrigatório/i)).toBeInTheDocument() })`  
  Component may render errors in different element or with different text
- **RegisterForm.test.tsx** line 93: Similar pattern with validation messages
- Tests don't verify error elements have proper ARIA labels or roles
- Some assertions check for error text that may be in hidden elements

**Pattern**: Tests use `waitFor` but assertions don't match actual DOM updates or element visibility

**Fix Strategy**:
- Verify exact error message text matches component implementation
- Check element visibility and focus state
- Add proper wait conditions for state changes

---

### 5. **DEBOUNCE & ASYNC STATE HANDLING - ~10-15 failures**
**Severity**: MEDIUM | **Impact**: SearchBar (10 failed), input change tests

**Root Cause**: Tests use `vi.useFakeTimers()` but component's debounce implementation or state updates don't align with test expectations.

**Evidence**:
- **SearchBar.test.tsx** lines 72-84: Debounce test with fake timers assumes immediate callback but:
  - Component's `handleChange` callback dependencies might not be aligned
  - The debounce timer cleanup might not work as expected in tests
  - Component state updates may not trigger at expected times
- Tests clear mocks but don't account for pending async operations

**Pattern**: Time-based tests fail due to timer mocking not matching actual async flow

**Fix Strategy**:
- Simplify debounce tests or use real timers with realistic delays
- Ensure component callback dependencies include all required variables
- Clear timers properly in beforeEach/afterEach hooks

---

## SECONDARY PATTERNS

### 6. **Role & Accessibility Attribute Mismatches (~5-8 failures)**
- Tests expect `role="searchbox"` but component may use `type="search"` instead
- Missing or incorrect ARIA labels and attributes
- Button role expectations don't match implementation

### 7. **Event Handler Expectations (~3-5 failures)**
- Tests check `toHaveBeenCalled()` but handlers may have different signatures
- Enter key handling tests expect specific behavior not implemented
- Click handler debouncing issues

---

## ROOT CAUSE DISTRIBUTION

| Pattern | Count | Files Affected |
|---------|-------|-----------------|
| CSS Class Mismatch | 35-40 | Input, Card, SearchBar, AnimalDetail |
| querySelector Issues | 20-25 | AnimalDetail, SearchBar, organisms |
| Mock Setup | 15-20 | LoginForm, RegisterForm, complex organisms |
| Form Validation Timing | 15-18 | LoginForm, RegisterForm |
| Debounce/Async | 10-15 | SearchBar, Input |
| Role/Accessibility | 5-8 | SearchBar, Button, organisms |
| Event Handlers | 3-5 | Various atoms/molecules |

---

## RECOMMENDED FIX ORDER

1. **First**: Fix CSS class expectations (Pattern #1)
   - Highest impact, affects 35-40 tests
   - Easiest to fix - just update class names in assertions
   - Time: ~2 hours

2. **Second**: Fix querySelector usage (Pattern #2)
   - Replace with React Testing Library queries
   - Time: ~1.5 hours

3. **Third**: Centralize mock setup (Pattern #3)
   - Create test utilities/wrapper components
   - Time: ~1 hour

4. **Fourth**: Fix form validation assertions (Pattern #4)
   - Update expected messages and timing
   - Time: ~1.5 hours

5. **Fifth**: Fix debounce tests (Pattern #5)
   - Simplify or rewrite async tests
   - Time: ~1 hour

**Total estimated fix time: ~7 hours**

---

## QUICK REFERENCE: CLASS NAME MAPPINGS

### Input Component
```
Expected (Test)          →  Actual (Component)
text-red-600            →  input-error (CSS)
text-gray-500           →  input-helper (CSS)
w-full                  →  input-wrapper (CSS)
```

### Card Component
```
Expected (Test)          →  Actual (Component)
bg-white                →  card (CSS)
rounded-lg              →  (part of card CSS)
shadow-md               →  (part of card CSS)
p-4                     →  (part of card CSS)
                        
Actual BEM classes:     
                        →  card
                        →  card--clickable
                        →  card__title
                        →  card__content
```

### SearchBar Component
```
Expected (Test)          →  Actual (Component)
search-input--error     →  search-input--error ✓ (correct)
search-bar              →  search-bar ✓ (correct)
But structure may differ on where these are applied
```

---

## ACTION ITEMS

- [ ] Update CSS assertion expectations in test files
- [ ] Replace querySelector with React Testing Library queries
- [ ] Create centralized test setup file with all providers/mocks
- [ ] Verify error message text in form components
- [ ] Simplify or rewrite debounce tests
- [ ] Run test suite after each fix group
- [ ] Document final CSS class conventions for future tests
