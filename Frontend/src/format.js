// The API sends money as strings like "35650.75" or "-800.25".
// We never convert them to JavaScript numbers (floats), so nothing is rounded.
// Intl.NumberFormat can format a decimal string exactly.
const numberFormat = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
})

// "35650.75" -> "35,650.75"      "-800.25" -> "(800.25)"
// Accountants show negative amounts in parentheses.
export function formatMoney(amount) {
    if (amount.startsWith('-')) {
        return `(${numberFormat.format(amount.slice(1))})`
    }
    return numberFormat.format(amount)
}

export function isNegative(amount) {
    return amount.startsWith('-')
}

// "2026-01-01" -> "Jan 1, 2026". Built by hand so time zones can't shift the day.
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
export function formatDate(isoDate) {
    const [year, month, day] = isoDate.split('-')
    return `${MONTHS[Number(month) - 1]} ${Number(day)}, ${year}`
}
