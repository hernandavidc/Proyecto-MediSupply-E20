# Configuración de Branch Protection Rules para GitHub

Esta configuración debe aplicarse manualmente en GitHub para bloquear merges cuando los tests fallan.

## 🛡️ Branch Protection Rules

### Configurar en GitHub Web Interface:

1. Ve a **Settings** → **Branches** → **Add rule**

2. **Branch name pattern**: `main`

3. **Configuraciones requeridas**:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: `1`
     - ✅ Dismiss stale PR approvals when new commits are pushed
     - ✅ Require review from code owners (opcional)
   
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - **Required status checks**:
       - `✅ Estado General`
       - `🧪 Tests User Service` (cuando hay cambios en user-service)
   
   - ✅ **Require conversation resolution before merging**
   - ✅ **Include administrators** (recomendado)
   - ✅ **Restrict pushes that create files** (recomendado)

4. **Save changes**

## 🔧 Configuración usando GitHub CLI (alternativa)

```bash
# Instalar GitHub CLI si no está instalado
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Autenticarse
gh auth login

# Configurar branch protection
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"checks":[{"context":"✅ Estado General"},{"context":"🧪 Tests User Service"}]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field required_conversation_resolution=true
```

## 🚀 Configuración usando Terraform (recomendado para equipos)

```hcl
resource "github_branch_protection" "main" {
  repository_id = var.repository_name
  pattern       = "main"

  required_status_checks {
    strict = true
    checks = [
      "✅ Estado General",
      "🧪 Tests User Service"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
    require_code_owner_reviews     = false
  }

  enforce_admins         = true
  allows_deletions       = false
  allows_force_pushes    = false
  require_signed_commits = false
}
```

## 📋 Checklist de Configuración

- [ ] Branch protection rule creada para `main`
- [ ] Status checks requeridos configurados
- [ ] Pull request reviews requeridos
- [ ] Administrators incluidos en las reglas
- [ ] Tests automáticos funcionando en PR de prueba

## 🎯 Resultado Esperado

Una vez configurado:

1. **❌ Merge bloqueado** si tests fallan
2. **🟡 Merge pendiente** mientras tests se ejecutan  
3. **✅ Merge permitido** solo cuando todos los tests pasan
4. **📊 Comentarios automáticos** en PRs con resultados de tests
5. **🔍 Detección inteligente** de cambios por microservicio

## 🔮 Futuras Expansiones

Cuando agregues nuevos microservicios:

```yaml
# En .github/workflows/tests.yml
detect-changes:
  outputs:
    inventory-service: ${{ steps.changes.outputs.inventory-service }}
    order-service: ${{ steps.changes.outputs.order-service }}

# Agregar nuevo job de tests
test-inventory-service:
  name: 🧪 Tests Inventory Service
  # ... configuración similar
```

Y actualizar branch protection rules para incluir los nuevos status checks.
