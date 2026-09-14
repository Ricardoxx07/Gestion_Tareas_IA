import { BrowserRouter } from 'react-router-dom'
import { ToastProvider } from './components/common/ToastProvider'
import { AuthProvider } from './hooks/AuthProvider'
import { AppRouter } from './routes/AppRouter'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <AppRouter />
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
