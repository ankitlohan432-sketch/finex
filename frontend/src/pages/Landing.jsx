import React from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Shield, Zap, BarChart3, Brain, Lock } from 'lucide-react'

export default function Landing() {
  const navigate = useNavigate()

  const features = [
    {
      icon: <TrendingUp size={24} />,
      title: 'Real-Time Market Data',
      description: 'Live stock prices, top gainers/losers, and market trends from TwelveData API'
    },
    {
      icon: <BarChart3 size={24} />,
      title: 'Advanced Charts',
      description: 'Interactive candlestick, area, and line charts with multiple time intervals'
    },
    {
      icon: <Brain size={24} />,
      title: 'AI Chatbot',
      description: 'Smart financial assistant for stock recommendations and market insights'
    },
    {
      icon: <Shield size={24} />,
      title: 'Fraud Detection',
      description: 'Secure transactions with ML-based anomaly detection'
    },
    {
      icon: <Zap size={24} />,
      title: 'Portfolio Management',
      description: 'Track your investments and optimize your portfolio'
    },
    {
      icon: <Lock size={24} />,
      title: 'Bank-Grade Security',
      description: 'JWT authentication, encrypted passwords, and secure API endpoints'
    }
  ]

  return (
    <div style={{ background: 'var(--bg-base)', color: 'var(--text-primary)', overflow: 'hidden' }}>
      {/* Navigation */}
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '20px 40px',
        background: 'rgba(18,20,20,0.6)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid var(--border-light)',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--accent)', fontFamily: "'Lexend'" }}>
          💎 FINEX
        </div>
        <div style={{ display: 'flex', gap: 16 }}>
          <button onClick={() => navigate('/login')} style={{
            padding: '10px 20px',
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-primary)',
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 600,
            transition: 'all 0.3s',
          }} onMouseEnter={(e) => {
            e.target.style.background = 'rgba(0,229,255,0.1)'
            e.target.style.borderColor = 'var(--accent)'
          }} onMouseLeave={(e) => {
            e.target.style.background = 'rgba(255,255,255,0.04)'
            e.target.style.borderColor = 'var(--border)'
          }}>
            Login
          </button>
          <button onClick={() => navigate('/register')} style={{
            padding: '10px 20px',
            background: 'var(--accent)',
            border: 'none',
            borderRadius: 8,
            color: '#001f24',
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 700,
            transition: 'all 0.3s',
            boxShadow: '0 0 20px rgba(0,229,255,0.3)'
          }} onMouseEnter={(e) => {
            e.target.style.boxShadow = '0 0 30px rgba(0,229,255,0.5)'
            e.target.style.transform = 'translateY(-2px)'
          }} onMouseLeave={(e) => {
            e.target.style.boxShadow = '0 0 20px rgba(0,229,255,0.3)'
            e.target.style.transform = 'translateY(0)'
          }}>
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        minHeight: '90vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 40px',
        backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(0,229,255,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(0,229,160,0.06) 0%, transparent 50%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Animated background elements */}
        <div style={{
          position: 'absolute',
          width: 400,
          height: 400,
          background: 'radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          top: -100,
          right: -100,
          animation: 'float 6s ease-in-out infinite'
        }} />
        <div style={{
          position: 'absolute',
          width: 300,
          height: 300,
          background: 'radial-gradient(circle, rgba(0,229,160,0.08) 0%, transparent 70%)',
          borderRadius: '50%',
          bottom: -50,
          left: -50,
          animation: 'float 8s ease-in-out infinite'
        }} />

        <div style={{
          maxWidth: 1200,
          textAlign: 'center',
          position: 'relative',
          zIndex: 2
        }}>
          <div style={{
            display: 'inline-block',
            padding: '8px 16px',
            background: 'rgba(0,229,255,0.1)',
            border: '1px solid rgba(0,229,255,0.2)',
            borderRadius: 20,
            marginBottom: 24,
            color: 'var(--accent)',
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: 0.05,
            textTransform: 'uppercase'
          }}>
            🚀 Welcome to the Future of Finance
          </div>

          <h1 style={{
            fontSize: 64,
            fontWeight: 800,
            fontFamily: "'Lexend'",
            marginBottom: 24,
            lineHeight: 1.2,
            background: 'linear-gradient(135deg, var(--accent) 0%, var(--text-primary) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Smart Financial Platform for Modern Investors
          </h1>

          <p style={{
            fontSize: 18,
            color: 'var(--text-secondary)',
            maxWidth: 600,
            margin: '0 auto 40px',
            lineHeight: 1.6
          }}>
            Real-time market data, AI-powered insights, and advanced portfolio management in one beautiful interface.
          </p>

          <div style={{
            display: 'flex',
            gap: 16,
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button onClick={() => navigate('/register')} style={{
              padding: '14px 32px',
              background: 'var(--accent)',
              border: 'none',
              borderRadius: 10,
              color: '#001f24',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: 700,
              transition: 'all 0.3s',
              boxShadow: '0 0 30px rgba(0,229,255,0.3)'
            }} onMouseEnter={(e) => {
              e.target.style.boxShadow = '0 0 40px rgba(0,229,255,0.5)'
              e.target.style.transform = 'translateY(-4px)'
            }} onMouseLeave={(e) => {
              e.target.style.boxShadow = '0 0 30px rgba(0,229,255,0.3)'
              e.target.style.transform = 'translateY(0)'
            }}>
              Get Started Free →
            </button>
            <button onClick={() => navigate('/login')} style={{
              padding: '14px 32px',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              color: 'var(--text-primary)',
              cursor: 'pointer',
              fontSize: 16,
              fontWeight: 700,
              transition: 'all 0.3s'
            }} onMouseEnter={(e) => {
              e.target.style.background = 'rgba(0,229,255,0.1)'
              e.target.style.borderColor = 'var(--accent)'
            }} onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255,255,255,0.04)'
              e.target.style.borderColor = 'var(--border)'
            }}>
              Sign In
            </button>
          </div>

          {/* Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: 24,
            marginTop: 80,
            paddingTop: 40,
            borderTop: '1px solid var(--border-light)'
          }}>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>10K+</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Active Users</div>
            </div>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--success)' }}>$5B+</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Assets Tracked</div>
            </div>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--info)' }}>99.9%</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Uptime</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{
        padding: '100px 40px',
        background: 'var(--bg-primary)',
        borderTop: '1px solid var(--border-light)'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 80 }}>
            <h2 style={{
              fontSize: 48,
              fontWeight: 800,
              fontFamily: "'Lexend'",
              marginBottom: 16
            }}>
              Powerful Features
            </h2>
            <p style={{
              fontSize: 18,
              color: 'var(--text-secondary)',
              maxWidth: 500,
              margin: '0 auto'
            }}>
              Everything you need to succeed in modern finance
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 24
          }}>
            {features.map((feature, idx) => (
              <div key={idx} style={{
                background: 'var(--glass-bg)',
                backdropFilter: 'var(--glass-blur)',
                border: '1px solid var(--glass-border)',
                borderRadius: 16,
                padding: 32,
                transition: 'all 0.3s',
                cursor: 'pointer',
                position: 'relative',
                overflow: 'hidden'
              }} onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-8px)'
                e.currentTarget.style.borderColor = 'rgba(0,229,255,0.3)'
                e.currentTarget.style.boxShadow = 'var(--shadow-hover)'
              }} onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.borderColor = 'var(--glass-border)'
                e.currentTarget.style.boxShadow = 'none'
              }}>
                <div style={{
                  width: 48,
                  height: 48,
                  background: 'rgba(0,229,255,0.1)',
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 16,
                  color: 'var(--accent)'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{
                  fontSize: 18,
                  fontWeight: 700,
                  marginBottom: 8,
                  fontFamily: "'Lexend'"
                }}>
                  {feature.title}
                </h3>
                <p style={{
                  fontSize: 14,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6
                }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{
        padding: '100px 40px',
        background: 'radial-gradient(circle at 50% 50%, rgba(0,229,255,0.08) 0%, transparent 100%)',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          <h2 style={{
            fontSize: 48,
            fontWeight: 800,
            fontFamily: "'Lexend'",
            marginBottom: 24
          }}>
            Ready to Transform Your Portfolio?
          </h2>
          <p style={{
            fontSize: 18,
            color: 'var(--text-secondary)',
            marginBottom: 32,
            lineHeight: 1.6
          }}>
            Join thousands of investors using FINEX to make smarter financial decisions.
          </p>
          <button onClick={() => navigate('/register')} style={{
            padding: '16px 40px',
            background: 'var(--accent)',
            border: 'none',
            borderRadius: 10,
            color: '#001f24',
            cursor: 'pointer',
            fontSize: 16,
            fontWeight: 700,
            transition: 'all 0.3s',
            boxShadow: '0 0 40px rgba(0,229,255,0.4)'
          }} onMouseEnter={(e) => {
            e.target.style.boxShadow = '0 0 50px rgba(0,229,255,0.6)'
            e.target.style.transform = 'translateY(-4px)'
          }} onMouseLeave={(e) => {
            e.target.style.boxShadow = '0 0 40px rgba(0,229,255,0.4)'
            e.target.style.transform = 'translateY(0)'
          }}>
            Start Your Journey Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '40px',
        background: 'var(--bg-primary)',
        borderTop: '1px solid var(--border-light)',
        textAlign: 'center',
        fontSize: 12,
        color: 'var(--text-muted)'
      }}>
        <p>© 2024 FINEX. All rights reserved. | Privacy Policy | Terms of Service</p>
      </footer>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(20px); }
        }
      `}</style>
    </div>
  )
}
