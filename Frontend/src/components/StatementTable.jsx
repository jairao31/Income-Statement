import Box from '@mui/material/Box'
import Paper from '@mui/material/Paper'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableRow from '@mui/material/TableRow'
import { formatMoney, isNegative } from '../format'

// Style shared by the main total rows (Total revenue, Gross profit, ...).
const highlight = { bgcolor: 'grey.100', fontWeight: 'bold' }

// Right-aligned amount. Negative amounts are red (formatMoney adds the parentheses).
// doubleUnderline draws the accounting double line under the figure itself,
// ending at the same right edge as the other amounts.
function Amount({ value, bold, doubleUnderline }) {
    return (
        <TableCell
            align="right"
            sx={{
                color: isNegative(value) ? 'error.main' : 'inherit',
                fontWeight: bold ? 'bold' : 'normal',
            }}
        >
            {doubleUnderline ? (
                <Box
                    component="span"
                    sx={{
                        display: 'inline-block',
                        borderBottom: '4px double',
                        borderColor: 'text.primary',
                    }}
                >
                    {formatMoney(value)}
                </Box>
            ) : (
                formatMoney(value)
            )}
        </TableCell>
    )
}

// A section built from accounts: Revenue, Cost of goods sold, Operating expenses, Other income.
// Every section looks the same:
//
//   Revenue                    heading
//   Product Revenue            one row per account
//   Total revenue              total row
function SectionRows({ section }) {
    const totalStyle = section.key === 'revenue' ? highlight : { fontWeight: 'bold' }

    return (
        <>
            <TableRow>
                <TableCell colSpan={2} sx={{ fontWeight: 'bold' }}>
                    {section.title}
                </TableCell>
            </TableRow>

            {section.lines.map((line) => (
                <TableRow key={line.account}>
                    <TableCell>
                        {/* Indent account names under their section heading */}
                        <Box component="span" sx={{ pl: 3 }}>
                            {line.name}
                        </Box>
                    </TableCell>
                    <Amount value={line.amount} />
                </TableRow>
            ))}

            <TableRow sx={totalStyle}>
                <TableCell sx={{ fontWeight: 'bold' }}>
                    Total {section.title.toLowerCase()}
                </TableCell>
                <Amount value={section.total} bold />
            </TableRow>
        </>
    )
}

// A calculated result: Gross profit, Operating income, Net income.
// Net income, the bottom line, gets the accounting double underline.
function ResultRow({ section }) {
    return (
        <TableRow sx={highlight}>
            <TableCell sx={{ fontWeight: 'bold' }}>{section.title}</TableCell>
            <Amount value={section.total} bold doubleUnderline={section.key === 'net_income'} />
        </TableRow>
    )
}

export default function StatementTable({ statement }) {
    return (
        <TableContainer component={Paper} variant="outlined">
            <Table sx={{ '& .MuiTableCell-root': { px: 4 } }}>
                <TableBody>
                    {statement.sections.map((section) =>
                        section.kind === 'accounts' ? (
                            <SectionRows key={section.key} section={section} />
                        ) : (
                            <ResultRow key={section.key} section={section} />
                        ),
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
