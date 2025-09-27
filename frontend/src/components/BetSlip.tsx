import React, { useState } from 'react'
import { api, type Edge } from '@/services/api'
import { BETA_VIEW_ONLY, BETA_DISCLAIMER, BETA_WARNING_TITLE } from '@/config/beta'

interface BetSlipProps {
  edge: Edge
  onClose: () => void
  onSuccess: () => void
}

export const BetSlip: React.FC<BetSlipProps> = ({ edge, onClose, onSuccess }) => {
  const viewOnly = BETA_VIEW_ONLY
  const [stake, setStake] = useState<string>('50')
  const [placing, setPlacing] = useState(false)
  const safetyNotice = BETA_DISCLAIMER
  const heading = viewOnly ? BETA_WARNING_TITLE : 'Place Bet'
  const [error, setError] = useState<string>('')

  const handlePlaceBet = async () => {
    if (viewOnly) {
      setError('Bet placement is disabled while we are in beta view-only mode.')
      return
    }

    const parsedStake = Number.parseFloat(stake)
    if (Number.isNaN(parsedStake) || parsedStake <= 0) {
      setError('Enter a valid stake amount greater than zero.')
      return
    }

    setPlacing(true)
    setError('')

    try {
      const selection = edge.recommendation.includes('UNDER') ? 'UNDER' : 'OVER'

      const response = await api.placeBet({
        game_id: edge.id.replace('edge_', ''),
        market: 'total',
        selection,
        line: edge.line,
        odds: -110,
        stake: parsedStake,
        bookmaker: edge.bookmaker,
      })

      if (response.success) {
        alert(`✅ Bet Placed Successfully!\n${response.message}`)
        onSuccess()
        onClose()
      }
    } catch (err) {
      setError('Failed to place bet. Please try again.')
      console.error(err)
    } finally {
      setPlacing(false)
    }
  }

  const numericStake = Number.parseFloat(stake) || 0
  const potentialWin = numericStake * (100 / 110)
  const potentialPayout = numericStake + potentialWin

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-xl font-bold">{heading}</h2>

        {viewOnly && (
          <div className="mb-4 rounded border-l-4 border-yellow-500 bg-yellow-50 p-3 text-sm text-yellow-800" role="note">
            {safetyNotice}
          </div>
        )}

        <div className="mb-4">
          <p className="font-semibold">{edge.game}</p>
          <p className="text-lg">{edge.recommendation}</p>
          <p className="text-sm text-gray-600">@ {edge.bookmaker}</p>
        </div>

        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium">
            Stake Amount ($)
          </label>
          <input
            type="number"
            value={stake}
            onChange={(event) => setStake(event.target.value)}
            className="w-full rounded-md border px-3 py-2"
            min="1"
            step="10"
          />
        </div>

        <div className="mb-4 rounded bg-gray-100 p-3">
          <div className="mb-2 flex justify-between">
            <span>Stake:</span>
            <span>${numericStake.toFixed(2)}</span>
          </div>
          <div className="mb-2 flex justify-between">
            <span>Odds:</span>
            <span>-110</span>
          </div>
          <div className="mb-2 flex justify-between">
            <span>Potential Win:</span>
            <span className="text-green-600">${potentialWin.toFixed(2)}</span>
          </div>
          <div className="flex justify-between font-bold">
            <span>Total Payout:</span>
            <span>${potentialPayout.toFixed(2)}</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded bg-red-100 p-2 text-red-700">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={handlePlaceBet}
            disabled={placing}
            className="flex-1 rounded-md bg-green-600 py-2 text-white transition hover:bg-green-700 disabled:opacity-50"
          >
            {placing ? 'Placing…' : 'Confirm Bet'}
          </button>
          <button
            onClick={onClose}
            disabled={placing}
            className="flex-1 rounded-md bg-gray-300 py-2 text-gray-700 transition hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
