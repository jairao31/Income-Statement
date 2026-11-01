import CloseIcon from '@mui/icons-material/Close'
import SearchIcon from '@mui/icons-material/Search'
import Chip from '@mui/material/Chip'
import IconButton from '@mui/material/IconButton'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import { PRESETS } from '../presets'

// The start and end date pickers, a Search button and a clear (X) button.
// Typing in the date fields does nothing by itself. The statement is only loaded
// when Search is clicked (or Enter is pressed), and Search needs both dates.
export function DateInputs({ start, end, onChange, onSearch, onClear }) {
    function handleSubmit(event) {
        event.preventDefault() // stop the browser from reloading the page
        onSearch()
    }

    return (
        <Stack
            component="form"
            onSubmit={handleSubmit}
            direction="row"
            spacing={1}
            useFlexGap
            sx={{
                alignItems: 'center',
                justifyContent: 'flex-end',
                flexWrap: 'wrap',
                maxWidth: '100%',
            }}
        >
            <TextField
                label="Start date"
                type="date"
                size="small"
                value={start}
                onChange={(e) => onChange(e.target.value, end)}
                slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
                label="End date"
                type="date"
                size="small"
                value={end}
                onChange={(e) => onChange(start, e.target.value)}
                slotProps={{ inputLabel: { shrink: true } }}
            />
            <IconButton type="submit" aria-label="Search" color="primary" disabled={!start || !end}>
                <SearchIcon />
            </IconButton>
            <IconButton
                type="button"
                aria-label="Clear dates"
                onClick={onClear}
                disabled={!start && !end}
            >
                <CloseIcon />
            </IconButton>
        </Stack>
    )
}

// One-click date ranges. Clicking one loads that range straight away.
// `start` and `end` here are the range currently loaded, so the matching chip is highlighted.
export function QuickSelect({ start, end, onChange }) {
    return (
        <Stack
            direction="row"
            spacing={1}
            useFlexGap
            sx={{
                alignItems: 'center',
                justifyContent: 'flex-end',
                flexWrap: 'wrap',
                maxWidth: '100%',
            }}
        >
            {PRESETS.map((preset) => {
                const active = preset.start === start && preset.end === end
                return (
                    <Chip
                        key={preset.label}
                        label={preset.label}
                        color={active ? 'primary' : 'default'}
                        onClick={() => onChange(preset.start, preset.end)}
                    />
                )
            })}
        </Stack>
    )
}
