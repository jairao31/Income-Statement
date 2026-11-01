import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import CssBaseline from '@mui/material/CssBaseline'
import '@fontsource/roboto/400.css'
import '@fontsource/roboto/500.css'
import '@fontsource/roboto/700.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <CssBaseline />
        <App />
    </StrictMode>,
)
