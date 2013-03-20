#global define
define [
  "jquery"
  "mustache"
  "text!edwareConfidenceLevelBarTemplate"
], ($, Mustache, confidenceLevelBarTemplate) ->
   
  #
  #    * Confidence level bar widget
  #    * Generate confidence level bar and calculate cutpoint pixel width, score position, score interval position
  #    * @param items - data for the confidence level bar
  #    * @param barWidth - Width of the bar in pixel
  #    
  $.fn.confidenceLevelBar = (items, barWidth) ->
      
      #Total bar width
      bar_width = barWidth
      
      #score indicator image width
      score_indicator_width = 13
      
      # Last cut point of the assessment
      items.last_interval = items.cut_point_intervals[items.cut_point_intervals.length-1]
      
      items.score_min_max_difference =  items.asmt_score_max - items.asmt_score_min
      
      # Calculate width for first cutpoint
      items.cut_point_intervals[0].asmt_cut_point =  Math.round(((items.cut_point_intervals[0].interval - items.asmt_score_min) / items.score_min_max_difference) * bar_width)
      
      # Calculate width for last cutpoint
      items.last_interval.asmt_cut_point =  Math.round(((items.last_interval.interval - items.cut_point_intervals[items.cut_point_intervals.length-2].interval) / items.score_min_max_difference) * bar_width)
      
      # Calculate width for cutpoints other than first and last cutpoints
      j = 1     
      while j < items.cut_point_intervals.length - 1
        items.cut_point_intervals[j].asmt_cut_point =  Math.round(((items.cut_point_intervals[j].interval - items.cut_point_intervals[j-1].interval) / items.score_min_max_difference) * bar_width)
        j++
      
      # Calculate position for indicator
      items.asmt_score_pos = Math.round(((items.asmt_score - items.asmt_score_min) / items.score_min_max_difference) * bar_width) - (score_indicator_width / 2)
      
      # Set position for left bracket
      items.asmt_score_min_range = Math.round(bar_width - (((items.asmt_score - items.asmt_score_min - items.asmt_score_interval) / items.score_min_max_difference) * bar_width))
      
      # Set position for right bracket
      items.asmt_score_max_range = Math.round((((items.asmt_score - items.asmt_score_min) + items.asmt_score_interval) / items.score_min_max_difference) * bar_width) 
      
      # Set "confidence interval" text on right hand side if maximum score range position is more than 80%
      items.leftBracketConfidenceLevel = items.asmt_score_max_range <= 580
      
      # use mustache template to display the json data  
      output = Mustache.to_html confidenceLevelBarTemplate, items
      this.html output
      
      # Align the score text to the center of indicator
      score_text_element = $(this).find(".overall_score")
      score_width = (score_text_element.width() / 2)
      #score_text_pos = Math.round(((items.asmt_score - items.asmt_score_min - score_width) / items.score_min_max_difference) * 100)
      score_text_pos = (items.asmt_score_pos - score_width) + (score_indicator_width / 2)
      score_text_element.css "margin-left", score_text_pos + "px"
      
  create = (containerId, data, barWidth) ->
    
     $(containerId).confidenceLevelBar data, barWidth

  create: create