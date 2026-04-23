/**
 * Simulador de fluxo de login e esqueci senha
 * Testa o fluxo sem precisar de um usuário autenticado
 */

// Script para limpar localStorage e fazer redirect
window.clearAuthAndRedirect = function(path = '/login') {
  localStorage.clear()
  sessionStorage.clear()
  window.location.href = `http://localhost:5173${path}`
}

// Executar no console do navegador:
// window.clearAuthAndRedirect('/login')
console.log('Para testar o fluxo de login, execute no console:')
console.log('window.clearAuthAndRedirect("/login")')
console.log('')
console.log('Para testar o fluxo de esqueci senha, execute:')
console.log('window.clearAuthAndRedirect("/esqueci-senha")')
console.log('')
console.log('Para fazer logout e ir para login:')
console.log('window.clearAuthAndRedirect()')
