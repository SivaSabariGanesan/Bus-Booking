"use client"

import React, { useState } from "react"
import { Link } from "react-router-dom"
import { MenuIcon, X } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { logout } from "../services/api"
import logo from "../../reclogo.webp"

interface HoveredLinkProps {
  children: React.ReactNode
  href: string
  [key: string]: unknown
}

const HoveredLink = ({ children, href, ...rest }: HoveredLinkProps) => {
  return (
    <Link
      {...rest}
      to={href}
      className="text-gray-700 hover:text-purple-600 transition-colors duration-200"
    >
      {children}
    </Link>
  )
}

interface NavbarProps {
  className?: string
}

const Navbar: React.FC<NavbarProps> = ({ className }) => {
  const [active, setActive] = useState<string | null>(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  useAuth()

  const handleLogout = async () => {
    try {
      await logout()
      // The logout function should handle clearing auth state
      window.location.href = '/login'
    } catch (error) {
      console.error('Logout failed:', error)
      // Force redirect even if logout fails
      window.location.href = '/login'
    }
  }

  return (
    <>
      {/* Desktop Navbar */}
      <div
        className={`navbar fixed top-2 sm:top-3 md:top-4 lg:top-4 xl:top-5 inset-x-0 max-w-xs sm:max-w-sm md:max-w-2xl lg:max-w-6xl xl:max-w-7xl mx-auto z-50 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 hidden md:block ${className || ""}`}
        onMouseLeave={() => setActive(null)}
      >
        <div className="relative rounded-full border border-gray-200 bg-white/95 backdrop-blur-md shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-between px-3 sm:px-4 lg:px-6 xl:px-8 py-1 sm:py-1.5 lg:py-1.5 xl:py-2">
          {/* Logo Section */}
          <div className="flex items-center flex-shrink-0">
            <Link to="/" className="flex items-center">
              <img
                src={logo}
                alt="REC Logo"
                className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 lg:w-14 lg:h-14 xl:w-16 xl:h-16 object-contain"
              />
            </Link>
          </div>

          <div className="w-12 sm:w-14 md:w-16 lg:w-14 xl:w-16 flex-shrink-0"></div>

          {/* Account Dropdown - Right Side */}
          <div className="flex items-center">
            <div className="relative">
              <button
                onClick={() => setActive(active === "Account" ? null : "Account")}
                className="p-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
                aria-label="Open menu"
              >
                <MenuIcon size={20} className="text-gray-700 navbar-icon" />
              </button>
              {active === "Account" && (
                <div className="absolute top-[calc(100%_+_1.2rem)] right-0 pt-4 animate-in fade-in-0 slide-in-from-top-2 duration-200">
                  <div className="bg-white backdrop-blur-sm rounded-2xl overflow-hidden border border-gray-200 shadow-xl min-w-[220px]">
                    <div className="p-4">
                      <div className="flex flex-col space-y-3 text-sm">
                        {/* Student menu */}
                        <HoveredLink href="/profile">Profile</HoveredLink>
                        <HoveredLink href="/my-booking">My Booking</HoveredLink>

                        <button
                          onClick={handleLogout}
                          className="text-left text-gray-700 hover:text-red-600 transition-colors duration-200"
                        >
                          Logout
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navbar */}
      <div className="navbar fixed top-4 left-4 right-4 z-50 md:hidden" onMouseLeave={() => setActive(null)}>
        <div className="relative bg-white/95 backdrop-blur-md rounded-full border border-gray-200 shadow-lg px-4 py-3 flex items-center justify-between">
          {/* Mobile Logo */}
          <Link to="/" className="flex items-center">
            <img
              src={logo}
              alt="REC Logo"
              className="w-14 h-14 sm:w-16 sm:h-16 object-contain"
            />
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors duration-200"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X size={20} className="text-gray-700 navbar-icon" />
            ) : (
              <MenuIcon size={20} className="text-gray-700 navbar-icon" />
            )}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <>
            <div className="fixed inset-0 bg-black/20 z-30" onClick={() => setIsMobileMenuOpen(false)} />
            <div className="absolute top-full left-0 right-0 mt-4 bg-white/95 backdrop-blur-md rounded-2xl border border-gray-200 shadow-xl p-4 max-h-[70vh] overflow-y-auto animate-in fade-in-0 slide-in-from-top-2 duration-300 z-40">
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold text-black-600 mb-3 text-base">Menu</h3>
                                     <div className="space-y-2 pl-4">
                     <div className="py-2">
                       <Link to="/" className="text-gray-700 hover:text-black transition-colors duration-200">
                         Home
                       </Link>
                     </div>
                     <div className="py-2">
                       <Link to="/profile" className="text-gray-700 hover:text-black transition-colors duration-200">
                         Profile
                       </Link>
                     </div>
                     <div className="py-2">
                       <Link to="/my-booking" className="text-gray-700 hover:text-black transition-colors duration-200">
                         My Booking
                       </Link>
                     </div>
                     <div className="py-2">

                     </div>
                     <div className="py-2">
                       <button
                         onClick={handleLogout}
                         className="text-gray-700 hover:text-red-600 transition-colors duration-200 w-full text-left"
                       >
                         Logout
                       </button>
                     </div>
                   </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}

export default Navbar 