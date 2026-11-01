import Alert from '@mui/material/Alert'
import CircularProgress from '@mui/material/CircularProgress'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useEffect, useRef, useState } from 'react'
import { fetchIncomeStatement } from './api'
import { DateInputs, QuickSelect } from './components/DateRangeBar'
import StatementTable from './components/StatementTable'
import { formatDate } from './format'
import { PRESETS } from './presets'

export default function App() {
    // Typed dates. Changing these does not load anything. Opens on Q1 2026.
    const [start, setStart] = useState(PRESETS[0].start)
    const [end, setEnd] = useState(PRESETS[0].end)

    const [statement, setStatement] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    // The request in flight, so a newer one can cancel it.
    const request = useRef(null)

    useEffect(() => {
        loadRange(PRESETS[0].start, PRESETS[0].end)
        return () => request.current.abort()
    }, [])

    function loadRange(from, to) {
        request.current?.abort() // an old response can never overwrite a newer one
        request.current = new AbortController()
        setError('')
        setLoading(true)

        fetchIncomeStatement(from, to, request.current.signal)
            .then((data) => {
                setStatement(data)
                setLoading(false)
            })
            .catch((err) => {
                if (err.name === 'AbortError') return
                setStatement(null) // do not leave stale numbers on screen
                setError(err.message)
                setLoading(false)
            })
    }

    // Empty the page, with an optional error message.
    function resetStatement(message = '') {
        request.current?.abort()
        setStatement(null)
        setLoading(false)
        setError(message)
    }

    function handleDateChange(newStart, newEnd) {
        setStart(newStart)
        setEnd(newEnd)
        setError('')
    }

    // Search button (or Enter): needs both dates, with start not after end.
    function handleSearch() {
        if (!start || !end) {
            resetStatement('Choose both a start and an end date.')
        } else if (start > end) {
            resetStatement('Start date must not be after the end date.')
        } else {
            loadRange(start, end)
        }
    }

    function handleQuickSelect(newStart, newEnd) {
        setStart(newStart)
        setEnd(newEnd)
        loadRange(newStart, newEnd)
    }

    function handleClear() {
        setStart('')
        setEnd('')
        resetStatement()
    }

    // Every line is exactly "0.00" (compared as text, never as numbers).
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
                    <QuickSelect start={start} end={end} onChange={handleQuickSelect} />
                </Stack>

                {/* Company, period and currency are shown only while a statement is loaded. */}
                {statement && (
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

                {error && <Alert severity="error">{error}</Alert>}

                {!statement && !loading && !error && (
                    <Alert severity="info">
                        Choose a start and an end date, then click search, or pick a quick select
                        range.
                    </Alert>
                )}

                {loading && !statement && <CircularProgress sx={{ alignSelf: 'center' }} />}

                {/* While reloading, keep showing the previous statement, dimmed. */}
                {statement && (
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
