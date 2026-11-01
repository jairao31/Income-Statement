import Alert from '@mui/material/Alert'
import CircularProgress from '@mui/material/CircularProgress'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useEffect, useState } from 'react'
import { fetchIncomeStatement } from './api'
import { DateInputs, QuickSelect } from './components/DateRangeBar'
import StatementTable from './components/StatementTable'
import { formatDate } from './format'
import { PRESETS } from './presets'

export default function App() {
    // What is typed in the two date fields. Changing these does not load anything.
    // The page opens on Q1 2026, the period the assessment asks about.
    const [start, setStart] = useState(PRESETS[0].start)
    const [end, setEnd] = useState(PRESETS[0].end)

    // The range that is actually loaded. It changes only when Search or a Quick select
    // chip is clicked, or when the dates are cleared. `n` goes up on every click, so
    // clicking Search again with the same dates loads the statement again.
    const [applied, setApplied] = useState({ start: PRESETS[0].start, end: PRESETS[0].end, n: 0 })

    const [statement, setStatement] = useState(null)
    // The outcome of the latest request, tagged with the dates it was for.
    const [result, setResult] = useState({ key: '', error: '' })
    // A problem with the typed dates, found when Search is clicked.
    const [inputError, setInputError] = useState('')

    const key = `${applied.start}|${applied.end}`

    // Dates cleared on purpose (X button): nothing to show, and not an error.
    const cleared = !applied.start

    // Still loading while the latest result is for a different range than the loaded one.
    const loading = !cleared && result.key !== key
    const error = result.key === key ? result.error : ''

    // Load the statement whenever the applied range changes.
    useEffect(() => {
        if (cleared) return

        // If another request starts before this one finishes, cancel this one
        // so an older response can never overwrite a newer one.
        const controller = new AbortController()

        fetchIncomeStatement(applied.start, applied.end, controller.signal)
            .then((data) => {
                setStatement(data)
                setResult({ key, error: '' })
            })
            .catch((err) => {
                if (err.name === 'AbortError') return
                // The request failed: drop the old statement so stale numbers are not shown.
                setStatement(null)
                setResult({ key, error: err.message })
            })

        return () => controller.abort()
    }, [applied, cleared, key])

    // Load a range now.
    function loadRange(newStart, newEnd) {
        setInputError('')
        setResult({ key: '', error: '' }) // shows the loading state, even for the same dates
        setApplied((previous) => ({ start: newStart, end: newEnd, n: previous.n + 1 }))
    }

    // Typing in the date fields only updates the fields.
    function handleDateChange(newStart, newEnd) {
        setStart(newStart)
        setEnd(newEnd)
        setInputError('')
    }

    // The typed dates are not valid: show the error and clear the statement,
    // so numbers for some other range are not left on screen under an error.
    function rejectInput(message) {
        setInputError(message)
        setStatement(null)
        setApplied((previous) => ({ start: '', end: '', n: previous.n + 1 }))
    }

    // Search button (or Enter): needs both dates, with start not after end.
    function handleSearch() {
        if (!start || !end) {
            rejectInput('Choose both a start and an end date.')
        } else if (start > end) {
            rejectInput('Start date must not be after the end date.')
        } else {
            loadRange(start, end)
        }
    }

    // Quick select chip: fill the fields and load straight away.
    function handleQuickSelect(newStart, newEnd) {
        setStart(newStart)
        setEnd(newEnd)
        loadRange(newStart, newEnd)
    }

    // X button: empty the fields and the statement.
    function handleClear() {
        setStart('')
        setEnd('')
        setInputError('')
        setApplied((previous) => ({ start: '', end: '', n: previous.n + 1 }))
    }

    const message = inputError || error

    // True when every account line is exactly "0.00" (compared as text, never as numbers).
    const allZero =
        statement !== null &&
        statement.sections.every((section) => section.lines.every((line) => line.amount === '0.00'))

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Stack spacing={3}>
                {/* Title on the left, date pickers on the right */}
                <Stack
                    direction="row"
                    spacing={2}
                    useFlexGap
                    sx={{ alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}
                >
                    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
                        <img src="/favicon.svg" alt="" width={40} height={40} />
                        <Typography variant="h4" component="h1">
                            Income Statement
                        </Typography>
                    </Stack>
                    <DateInputs
                        start={start}
                        end={end}
                        onChange={handleDateChange}
                        onSearch={handleSearch}
                        onClear={handleClear}
                    />
                </Stack>

                {/* Quick select below, aligned to the right */}
                <Stack sx={{ alignItems: 'flex-end' }}>
                    <QuickSelect
                        start={applied.start}
                        end={applied.end}
                        onChange={handleQuickSelect}
                    />
                </Stack>

                {/* Company, period and currency are shown only while a statement is loaded. */}
                {statement && !cleared && (
                    <Stack
                        direction="row"
                        spacing={1.5}
                        divider={
                            <Divider
                                orientation="vertical"
                                flexItem
                                sx={{ borderColor: 'grey.500' }}
                            />
                        }
                        sx={{ alignItems: 'center' }}
                    >
                        <Typography variant="h6">{statement.company}</Typography>
                        <Typography color="text.secondary">
                            {formatDate(statement.period.start)} –{' '}
                            {formatDate(statement.period.end)} · {statement.currency}
                        </Typography>
                    </Stack>
                )}

                {message && <Alert severity="error">{message}</Alert>}

                {cleared && !message && (
                    <Alert severity="info">
                        Choose a start and an end date, then click search, or pick a quick select
                        range.
                    </Alert>
                )}

                {loading && !statement && <CircularProgress sx={{ alignSelf: 'center' }} />}

                {/* While reloading, keep showing the previous statement, dimmed. */}
                {statement && !cleared && (
                    <Stack spacing={2} sx={{ opacity: loading ? 0.5 : 1 }}>
                        {/* A quiet period still shows the full table. The note just says it is not an error. */}
                        {allZero && (
                            <Alert severity="info">All amounts are zero for this period.</Alert>
                        )}
                        <StatementTable statement={statement} />
                    </Stack>
                )}
            </Stack>
        </Container>
    )
}
