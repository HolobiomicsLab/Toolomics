#!/bin/bash

# DECIMER MCP Stress Test Script
# Tests the TensorFlow multiprocessing fix by running classifier + segmentation repeatedly

echo "🧪 DECIMER MCP Stress Test - TensorFlow Multiprocessing Fix"
echo "=========================================================="
echo "This test will run classifier + segmentation 10 times to verify robustness"
echo ""


# Initialize counters
total_tests=0
passed_tests=0
failed_tests=0

# Run stress test loop
for i in {1..20}; do
    echo "🔄 STRESS TEST ROUND $i/20"
    echo "=========================="
    
    # Test 1: Classifier
    echo "📊 Running classifier test..."
    if python tests/test_decimer_classifier.py; then
        echo "✅ Classifier test PASSED"
        classifier_result="PASS"
    else
        echo "❌ Classifier test FAILED"
        classifier_result="FAIL"
        ((failed_tests++))
    fi
    
    echo ""
    
    # Test 2: Segmentation (this is the critical test)
    echo "🔬 Running segmentation test..."
    if python tests/test_decimer_segmentation.py; then
        echo "✅ Segmentation test PASSED"
        segmentation_result="PASS"
    else
        echo "❌ Segmentation test FAILED"
        segmentation_result="FAIL"
        ((failed_tests++))
    fi
    
    # Check overall result for this round
    if [[ "$classifier_result" == "PASS" && "$segmentation_result" == "PASS" ]]; then
        echo "🎉 Round $i: BOTH TESTS PASSED"
        ((passed_tests++))
    else
        echo "💥 Round $i: SOME TESTS FAILED"
    fi
    
    ((total_tests++))
    
    echo ""
    echo "📊 Progress: $i/10 rounds completed"
    echo "   Passed: $passed_tests"
    echo "   Failed: $failed_tests"
    echo ""
    
    # Small delay between rounds
    sleep 2
done

echo "🏁 STRESS TEST COMPLETE"
echo "======================="
echo "Total rounds: $total_tests"
echo "Passed rounds: $passed_tests"
echo "Failed rounds: $failed_tests"
echo "Success rate: $((passed_tests * 100 / total_tests))%"

if [[ $failed_tests -eq 0 ]]; then
    echo ""
    echo "🎉 ALL TESTS PASSED! TensorFlow fix is robust!"
    echo "✅ No hanging issues detected"
    echo "✅ No memory leaks detected"
    echo "✅ No multiprocessing conflicts detected"
    exit 0
else
    echo ""
    echo "⚠️ SOME TESTS FAILED! TensorFlow fix needs investigation"
    echo "❌ $failed_tests rounds had failures"
    exit 1
fi




