'use client'

import { useState } from 'react'
import { CreditCard, Plus, History, Zap, Star, Crown } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '@/hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import { userAPI, generationAPI } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function CreditsPage() {
  const { user } = useAuth()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  // Fetch credit transactions
  const { data: transactions, isLoading: loadingTransactions } = useQuery({
    queryKey: ['credit-transactions'],
    queryFn: () => generationAPI.getCreditTransactions().then(res => res.data.transactions),
  })

  // Fetch usage stats
  const { data: usageStats, isLoading: loadingStats } = useQuery({
    queryKey: ['usage-stats'],
    queryFn: () => userAPI.getUsageStats().then(res => res.data),
  })

  const creditPackages = [
    {
      id: 'starter',
      name: 'Starter Pack',
      credits: 50,
      price: 9.99,
      bonus: 0,
      popular: false,
      icon: <Zap className="w-6 h-6" />
    },
    {
      id: 'popular',
      name: 'Popular Pack',
      credits: 150,
      price: 24.99,
      bonus: 25,
      popular: true,
      icon: <Star className="w-6 h-6" />
    },
    {
      id: 'pro',
      name: 'Pro Pack',
      credits: 300,
      price: 49.99,
      bonus: 75,
      popular: false,
      icon: <Crown className="w-6 h-6" />
    }
  ]

  const handlePurchase = async (packageId: string) => {
    setSelectedPlan(packageId)
    // TODO: Implement payment integration
    console.log('Purchase package:', packageId)
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-thin bg-gray-50">
      <div className="max-w-6xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Credits & Billing
          </h1>
          <p className="text-gray-600">
            Manage your credits and purchase additional generation power
          </p>
        </div>

        {/* Current Balance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Current Balance</h2>
              <div className="flex items-center gap-2">
                <span className="text-4xl font-bold">{user?.credits || 0}</span>
                <span className="text-xl opacity-80">credits</span>
              </div>
              <p className="opacity-80 mt-2">
                Subscription: <span className="capitalize font-semibold">{user?.subscription_tier || 'free'}</span>
              </p>
            </div>
            
            <div className="text-right">
              <div className="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mb-4">
                <CreditCard className="w-8 h-8" />
              </div>
              <p className="text-sm opacity-80">
                1 credit = 1 basic generation
              </p>
            </div>
          </div>
        </motion.div>

        {/* Usage Stats */}
        {usageStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid md:grid-cols-4 gap-6"
          >
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-sm font-medium text-gray-600">Total Generations</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {usageStats.generations_by_status?.completed || 0}
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CreditCard className="w-5 h-5 text-green-600" />
                </div>
                <span className="text-sm font-medium text-gray-600">Credits Used</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {Math.abs(usageStats.credits_by_type?.usage || 0)}
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Plus className="w-5 h-5 text-purple-600" />
                </div>
                <span className="text-sm font-medium text-gray-600">Credits Purchased</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {usageStats.credits_by_type?.purchase || 0}
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                  <History className="w-5 h-5 text-orange-600" />
                </div>
                <span className="text-sm font-medium text-gray-600">This Month</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {usageStats.recent_activity?.generations_last_30_days || 0}
              </p>
            </div>
          </motion.div>
        )}

        {/* Credit Packages */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Purchase Credits
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            {creditPackages.map((pkg, index) => (
              <motion.div
                key={pkg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className={`relative bg-white rounded-2xl p-6 border-2 transition-all hover:shadow-lg ${
                  pkg.popular 
                    ? 'border-blue-500 shadow-lg scale-105' 
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                {pkg.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <div className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="text-center">
                  <div className={`w-12 h-12 mx-auto mb-4 rounded-xl flex items-center justify-center ${
                    pkg.popular ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {pkg.icon}
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {pkg.name}
                  </h3>

                  <div className="mb-4">
                    <span className="text-3xl font-bold text-gray-900">
                      ${pkg.price}
                    </span>
                  </div>

                  <div className="space-y-2 mb-6">
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-2xl font-bold text-blue-600">
                        {pkg.credits}
                      </span>
                      <span className="text-gray-600">credits</span>
                    </div>
                    
                    {pkg.bonus > 0 && (
                      <div className="text-sm text-green-600 font-medium">
                        + {pkg.bonus} bonus credits
                      </div>
                    )}
                    
                    <div className="text-xs text-gray-500">
                      ${(pkg.price / (pkg.credits + pkg.bonus)).toFixed(3)} per credit
                    </div>
                  </div>

                  <button
                    onClick={() => handlePurchase(pkg.id)}
                    disabled={selectedPlan === pkg.id}
                    className={`w-full py-3 rounded-xl font-semibold transition-colors ${
                      pkg.popular
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {selectedPlan === pkg.id ? 'Processing...' : 'Purchase'}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Transaction History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl p-6 border border-gray-200"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Transaction History
          </h2>

          {loadingTransactions ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg">
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-48" />
                    <div className="h-3 bg-gray-100 rounded animate-pulse w-32" />
                  </div>
                  <div className="h-6 bg-gray-200 rounded animate-pulse w-16" />
                </div>
              ))}
            </div>
          ) : transactions && transactions.length > 0 ? (
            <div className="space-y-3">
              {transactions.map((transaction: any) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      {transaction.description}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatDate(transaction.created_at)}
                    </p>
                  </div>
                  
                  <div className="text-right">
                    <span className={`font-semibold ${
                      transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                    </span>
                    <p className="text-xs text-gray-500 capitalize">
                      {transaction.type}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No transactions yet</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
