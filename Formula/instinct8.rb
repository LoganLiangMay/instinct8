# Homebrew Formula for Instinct8 Agent
# 
# To use this formula:
#   1. Create a GitHub repo: instinct8-homebrew
#   2. Copy this file to Formula/instinct8.rb in that repo
#   3. Users install with: brew tap jjjorgenson/instinct8 && brew install instinct8
#
# Or submit to Homebrew core for official inclusion

class Instinct8 < Formula
  desc "Instinct8 Agent - Coding agent with Selective Salience Compression"
  homepage "https://github.com/jjjorgenson/instinct8"
  url "https://files.pythonhosted.org/packages/source/i/instinct8-agent/instinct8-agent-0.1.0.tar.gz"
  # Calculate SHA256 with: shasum -a 256 dist/instinct8_agent-0.1.0.tar.gz
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "Apache-2.0"
  revision 0

  depends_on "python@3.9"

  def install
    # Install using pip
    system "python3", "-m", "pip", "install", "--prefix=#{prefix}", "--no-warn-script-location", "."
    
    # Ensure scripts are in PATH
    bin.install Dir["#{prefix}/bin/*"]
  end

  test do
    system "#{bin}/instinct8", "--help"
  end
end
